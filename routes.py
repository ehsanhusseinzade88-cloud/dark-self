from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from models import (Admin, User, Payment, AdminSettings, UserTextFormat, UserMediaLock,
                    UserStatusAction, UserTranslation, UserComment, UserSecretary,
                    UserAntiLogin, UserAutoReaction, EnemyList, FriendList, CrushList,
                    UserAnimationPreset, UserBlock, UserMute, SubscriptionChannel, Report)
from werkzeug.security import generate_password_hash, check_password_hash
from payment_handler import PaymentManager, GemDeductionScheduler
from functools import wraps
from datetime import datetime
from utils import get_all_features_menu, format_iran_time
from bson import ObjectId
import os

# Blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
admin_bp = Blueprint('admin', __name__)
user_bp = Blueprint('user', __name__)
payment_bp = Blueprint('payment', __name__)


# Authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============= AUTH ROUTES =============

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username')
        password = data.get('password')
        
        admin = Admin.objects(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = str(admin.id)
            session['admin_username'] = admin.username
            session.permanent = True
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'redirect': '/admin/dashboard'
            })
        
        return jsonify({
            'status': 'error',
            'message': 'Invalid credentials'
        }), 401
    
    return render_template('admin_login.html')


@auth_bp.route('/user/register', methods=['POST'])
def user_register():
    """User registration with phone number"""
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({'status': 'error', 'message': 'Phone number required'}), 400
    
    # Check if user already exists
    existing_user = User.objects(phone_number=phone_number).first()
    if existing_user:
        return jsonify({'status': 'error', 'message': 'User already exists'}), 400
    
    # Create new admin if first user
    admin = Admin.objects.first()
    if not admin:
        admin = Admin(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_active=True
        )
        admin.save()
    
    # Create user with pending status
    user = User(
        admin_id=admin.id,
        phone_number=phone_number,
        is_authenticated=False,
        is_verified=False,
        gems=0
    )
    user.save()
    
    # Store in session
    session['user_id'] = str(user.id)
    session['phone_number'] = phone_number
    session['user_step'] = 'phone_registered'
    
    return jsonify({
        'status': 'success',
        'user_id': str(user.id),
        'message': 'User registered. Please send phone code.',
        'next_step': 'send_code'
    })


@auth_bp.route('/user/start', methods=['POST'])
def user_start():
    """User starts and sends phone number"""
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    if not phone_number:
        return jsonify({'status': 'error', 'message': 'Phone number required'}), 400
    
    # Store in session temporarily
    session['phone_number'] = phone_number
    session['user_step'] = 'phone_sent'
    
    return jsonify({
        'status': 'success',
        'message': 'Phone number received. Please enter verification code.',
        'next_step': 'verify_code'
    })


@auth_bp.route('/user/verify-code', methods=['POST'])
def user_verify_code():
    """User verifies code"""
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({'status': 'error', 'message': 'Code required'}), 400
    
    # TODO: Integrate with Telegram authentication
    session['user_step'] = 'code_verified'
    session['verification_code'] = code
    
    return jsonify({
        'status': 'success',
        'message': 'Code verified',
        'next_step': 'setup_complete'
    })


@auth_bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    """Admin logout"""
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})


# ============= ADMIN ROUTES =============

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    admin_id = ObjectId(session.get('admin_id'))
    
    users_count = User.objects(admin_id=admin_id).count()
    
    # Get total gems sold from approved payments
    approved_payments = Payment.objects(status='approved')
    total_gems_sold = sum(p.gems for p in approved_payments) if approved_payments else 0
    
    pending_payments = Payment.objects(status='pending').count()
    
    return render_template('admin_dashboard.html', {
        'users_count': users_count,
        'total_gems_sold': total_gems_sold,
        'pending_payments': pending_payments
    })


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """Admin settings"""
    admin_id = ObjectId(session.get('admin_id'))
    admin = Admin.objects(id=admin_id).first()
    
    if request.method == 'POST':
        data = request.get_json()
        
        if admin:
            admin.settings.gem_price_toman = data.get('gem_price_toman', admin.settings.gem_price_toman)
            admin.settings.minimum_gems_activate = data.get('minimum_gems_activate', admin.settings.minimum_gems_activate)
            admin.settings.gems_per_hour = data.get('gems_per_hour', admin.settings.gems_per_hour)
            admin.settings.bank_card_number = data.get('bank_card_number', admin.settings.bank_card_number)
            admin.settings.bank_account_name = data.get('bank_account_name', admin.settings.bank_account_name)
            admin.settings.subscription_channel = data.get('subscription_channel', admin.settings.subscription_channel)
            admin.settings.require_subscription = data.get('require_subscription', False)
            admin.settings.updated_at = datetime.utcnow()
            admin.save()
        
        return jsonify({'status': 'success', 'message': 'Settings updated'})
    
    settings_data = admin.settings if admin else AdminSettings()
    return jsonify({
        'gem_price_toman': settings_data.gem_price_toman,
        'minimum_gems_activate': settings_data.minimum_gems_activate,
        'gems_per_hour': settings_data.gems_per_hour,
        'bank_card_number': settings_data.bank_card_number or '',
        'bank_account_name': settings_data.bank_account_name or '',
        'subscription_channel': settings_data.subscription_channel or '',
        'require_subscription': settings_data.require_subscription
    })


@admin_bp.route('/payments', methods=['GET'])
@admin_required
def payments_list():
    """Get all pending payments"""
    payments = PaymentManager.get_pending_payments()
    return jsonify({'payments': payments})


@admin_bp.route('/payment/<int:payment_id>/approve', methods=['POST'])
@admin_required
def approve_payment(payment_id):
    """Approve payment"""
    admin_id = session.get('admin_id')
    data = request.get_json()
    note = data.get('note', '')
    
    result = PaymentManager.approve_payment(payment_id, admin_id, note)
    return jsonify(result)


@admin_bp.route('/payment/<int:payment_id>/reject', methods=['POST'])
@admin_required
def reject_payment(payment_id):
    """Reject payment"""
    admin_id = session.get('admin_id')
    data = request.get_json()
    note = data.get('note', '')
    
    result = PaymentManager.reject_payment(payment_id, admin_id, note)
    return jsonify(result)


@admin_bp.route('/users', methods=['GET'])
@admin_required
def users_list():
    """Get all users"""
    admin_id = ObjectId(session.get('admin_id'))
    users = User.objects(admin_id=admin_id).all()
    
    return jsonify({
        'users': [{
            'id': str(u.id),
            'telegram_id': u.telegram_id,
            'username': u.username,
            'first_name': u.first_name,
            'gems': u.gems,
            'is_authenticated': u.is_authenticated,
            'created_at': u.created_at.isoformat()
        } for u in users]
    })


@admin_bp.route('/user/<user_id>/gems', methods=['POST'])
@admin_required
def add_gems_to_user(user_id):
    """Add gems to user"""
    data = request.get_json()
    gems_amount = data.get('gems', 0)
    reason = data.get('reason', 'Admin gift')
    
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    user.gems += gems_amount
    user.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Added {gems_amount} gems to user',
        'total_gems': user.gems
    })


# ============= USER ROUTES =============

@user_bp.route('/<user_id>/profile', methods=['GET'])
def user_profile(user_id):
    """Get user profile"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    return jsonify({
        'id': str(user.id),
        'telegram_id': user.telegram_id,
        'username': user.username,
        'first_name': user.first_name,
        'gems': user.gems,
        'gems_spent': user.gems_spent,
        'is_authenticated': user.is_authenticated,
        'features_enabled': user.features_enabled or {},
        'self_settings': user.self_settings or {}
    })


@user_bp.route('/<user_id>/features', methods=['GET', 'POST'])
def user_features(user_id):
    """Get/update user features"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'features': get_all_features_menu(),
            'enabled_features': user.features_enabled or {}
        })
    
    data = request.get_json()
    feature_name = data.get('feature')
    enabled = data.get('enabled')
    
    if not user.features_enabled:
        user.features_enabled = {}
    
    user.features_enabled[feature_name] = enabled
    user.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Feature {feature_name} {"enabled" if enabled else "disabled"}',
        'features': user.features_enabled
    })


@user_bp.route('/<user_id>/self/activate', methods=['POST'])
def activate_self(user_id):
    """Activate self-bot"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # Check if user is admin - admin gets free activation
    admin = Admin.objects(id=user.admin_id).first()
    is_admin = admin is not None
    
    if not is_admin:
        # Check minimum gems for non-admin users
        minimum_check = GemDeductionScheduler.check_minimum_gems(str(user.id))
        
        if not minimum_check['has_minimum']:
            return jsonify({
                'status': 'error',
                'message': f'You need {minimum_check["required"]} gems to activate. You have {minimum_check["gems"]}. You need {minimum_check["remaining"]} more.',
                'required': minimum_check['required'],
                'current': minimum_check['gems']
            }), 400
    
    # Activate time display
    user.time_enabled = True
    
    # Start gem deduction only for non-admin users
    if not is_admin:
        GemDeductionScheduler.start_deduction_for_user(str(user.id))
    
    user.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Self-bot activated successfully',
        'time_enabled': True,
        'gems_remaining': user.gems,
        'is_free': is_admin
    })


@user_bp.route('/<user_id>/self/deactivate', methods=['POST'])
def deactivate_self(user_id):
    """Deactivate self-bot"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # Deactivate and stop deduction
    GemDeductionScheduler.stop_deduction_for_user(str(user.id))
    
    user.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Self-bot deactivated'
    })


@user_bp.route('/<user_id>/time-font', methods=['POST'])
def set_time_font(user_id):
    """Set time font"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    font_id = data.get('font_id', 0)
    
    user.time_font = font_id
    user.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Time font set to style {font_id}',
        'current_time': format_iran_time(font_id=font_id)
    })


# ============= PAYMENT ROUTES =============

@payment_bp.route('/buy-gems', methods=['POST'])
def buy_gems():
    """Create gem purchase request"""
    data = request.get_json()
    user_id = data.get('user_id')
    gem_amount = data.get('gem_amount')
    
    if not user_id or not gem_amount:
        return jsonify({'status': 'error', 'message': 'Missing parameters'}), 400
    
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    # Create payment request
    payment_info = PaymentManager.create_payment_request(user_id, gem_amount)
    
    # Get settings for bank info
    admin = Admin.objects(id=user.admin_id).first()
    settings = admin.settings if admin else None
    
    return jsonify({
        'status': 'success',
        'payment_id': str(payment_info['payment_id']),
        'gems': payment_info['gems'],
        'amount_toman': payment_info['amount_toman'],
        'bank_card': settings.bank_card_number if settings else '',
        'account_name': settings.bank_account_name if settings else '',
        'next_step': 'transfer_payment'
    })


@payment_bp.route('/<int:payment_id>/upload-receipt', methods=['POST'])
def upload_receipt(payment_id):
    """Upload payment receipt"""
    if 'receipt' not in request.files:
        return jsonify({'status': 'error', 'message': 'No receipt file'}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    # Convert image to base64
    import base64
    image_data = base64.b64encode(file.read()).decode('utf-8')
    
    result = PaymentManager.upload_receipt(payment_id, image_data)
    return jsonify(result)


@payment_bp.route('/<payment_id>/status', methods=['GET'])
def payment_status(payment_id):
    """Get payment status"""
    try:
        payment = Payment.objects(id=ObjectId(payment_id)).first()
    except:
        payment = None
    
    if not payment:
        return jsonify({'status': 'error', 'message': 'Payment not found'}), 404
    
    return jsonify({
        'id': str(payment.id),
        'user_id': str(payment.user_id),
        'gems': payment.gems,
        'amount_toman': payment.amount_toman,
        'status': payment.status,
        'created_at': payment.created_at.isoformat(),
        'approved_at': payment.approved_at.isoformat() if payment.approved_at else None
    })


# ============= SELF-BOT FEATURE ROUTES =============

@user_bp.route('/<user_id>/text-format', methods=['POST'])
def toggle_text_format(user_id):
    """Toggle text formatting feature"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    format_type = data.get('format_type')  # bold, italic, etc
    enabled = data.get('enabled', False)
    
    fmt = UserTextFormat.objects(
        user_id=ObjectId(user_id),
        format_type=format_type
    ).first()
    
    if not fmt:
        fmt = UserTextFormat(
            user_id=ObjectId(user_id),
            format_type=format_type,
            is_enabled=enabled
        )
        fmt.save()
    else:
        fmt.is_enabled = enabled
        fmt.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Text format {format_type} {"enabled" if enabled else "disabled"}',
        'format_type': format_type,
        'is_enabled': enabled
    })


@user_bp.route('/<user_id>/media-lock', methods=['POST'])
def toggle_media_lock(user_id):
    """Toggle media lock in private messages"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    media_type = data.get('media_type')  # gif, photo, video, etc
    enabled = data.get('enabled', False)
    
    lock = UserMediaLock.objects(
        user_id=ObjectId(user_id),
        media_type=media_type
    ).first()
    
    if not lock:
        lock = UserMediaLock(
            user_id=ObjectId(user_id),
            media_type=media_type,
            is_enabled=enabled
        )
        lock.save()
    else:
        lock.is_enabled = enabled
        lock.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Media lock {media_type} {"enabled" if enabled else "disabled"}',
        'media_type': media_type
    })


@user_bp.route('/<user_id>/status-action', methods=['POST'])
def toggle_status_action(user_id):
    """Toggle status/action display"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    action_type = data.get('action_type')  # typing, playing, etc
    enabled = data.get('enabled', False)
    
    action = UserStatusAction.objects(
        user_id=ObjectId(user_id),
        action_type=action_type
    ).first()
    
    if not action:
        action = UserStatusAction(
            user_id=ObjectId(user_id),
            action_type=action_type,
            is_enabled=enabled
        )
        action.save()
    else:
        action.is_enabled = enabled
        action.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Status action {action_type} {"enabled" if enabled else "disabled"}'
    })


@user_bp.route('/<user_id>/translation', methods=['POST'])
def toggle_translation(user_id):
    """Toggle auto-translation feature"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    language = data.get('language')  # english, chinese, russian, etc
    enabled = data.get('enabled', False)
    
    trans = UserTranslation.objects(
        user_id=ObjectId(user_id),
        target_language=language
    ).first()
    
    if not trans:
        trans = UserTranslation(
            user_id=ObjectId(user_id),
            target_language=language,
            is_enabled=enabled
        )
        trans.save()
    else:
        trans.is_enabled = enabled
        trans.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Auto-translation to {language} {"enabled" if enabled else "disabled"}'
    })


@user_bp.route('/<user_id>/comment', methods=['POST'])
def set_comment(user_id):
    """Set comment text for forwarded messages"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    comment_text = data.get('comment_text')
    enabled = data.get('enabled', False)
    
    comment = UserComment.objects(user_id=ObjectId(user_id)).first()
    
    if not comment:
        comment = UserComment(
            user_id=ObjectId(user_id),
            comment_text=comment_text,
            is_enabled=enabled
        )
        comment.save()
    else:
        comment.comment_text = comment_text
        comment.is_enabled = enabled
        comment.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Comment text updated'
    })


@user_bp.route('/<user_id>/secretary', methods=['POST'])
def set_secretary(user_id):
    """Set secretary/auto-reply settings"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    reply_text = data.get('reply_text')
    enabled = data.get('enabled', False)
    use_ai = data.get('use_ai', False)
    
    secretary = UserSecretary.objects(user_id=ObjectId(user_id)).first()
    
    if not secretary:
        secretary = UserSecretary(
            user_id=ObjectId(user_id),
            auto_reply_text=reply_text,
            is_enabled=enabled,
            use_ai=use_ai
        )
        secretary.save()
    else:
        secretary.auto_reply_text = reply_text
        secretary.is_enabled = enabled
        secretary.use_ai = use_ai
        secretary.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Secretary settings updated'
    })


@user_bp.route('/<user_id>/anti-login', methods=['POST'])
def toggle_anti_login(user_id):
    """Toggle anti-login protection"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    enabled = data.get('enabled', False)
    
    anti_login = UserAntiLogin.objects(user_id=ObjectId(user_id)).first()
    
    if not anti_login:
        anti_login = UserAntiLogin(
            user_id=ObjectId(user_id),
            is_enabled=enabled,
            alert_on_login=True
        )
        anti_login.save()
    else:
        anti_login.is_enabled = enabled
        anti_login.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Anti-login {"enabled" if enabled else "disabled"}'
    })


@user_bp.route('/<user_id>/auto-reaction', methods=['POST'])
def set_auto_reaction(user_id):
    """Set auto-reaction emoji"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    emoji = data.get('emoji')
    enabled = data.get('enabled', False)
    
    reaction = UserAutoReaction.objects(user_id=ObjectId(user_id)).first()
    
    if not reaction:
        reaction = UserAutoReaction(
            user_id=ObjectId(user_id),
            emoji=emoji,
            is_enabled=enabled
        )
        reaction.save()
    else:
        reaction.emoji = emoji
        reaction.is_enabled = enabled
        reaction.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Auto-reaction set to {emoji}'
    })


@user_bp.route('/<user_id>/enemy-list', methods=['GET', 'POST', 'DELETE'])
def manage_enemy_list(user_id):
    """Manage enemy list"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    if request.method == 'GET':
        enemies = EnemyList.objects(user_id=ObjectId(user_id)).all()
        return jsonify({
            'enemies': [{
                'id': str(e.id),
                'target_id': e.target_id,
                'target_username': e.target_username,
                'is_enabled': e.is_enabled
            } for e in enemies]
        })
    
    data = request.get_json()
    
    if request.method == 'POST':
        target_id = data.get('target_id')
        target_username = data.get('target_username')
        
        enemy = EnemyList.objects(
            user_id=ObjectId(user_id),
            target_id=target_id
        ).first()
        
        if not enemy:
            enemy = EnemyList(
                user_id=ObjectId(user_id),
                target_id=target_id,
                target_username=target_username,
                is_enabled=True
            )
            enemy.save()
        else:
            enemy.is_enabled = not enemy.is_enabled
            enemy.save()
        
        return jsonify({'status': 'success', 'message': 'Enemy added/updated'})
    
    elif request.method == 'DELETE':
        enemy_id = data.get('enemy_id')
        EnemyList.objects(id=ObjectId(enemy_id), user_id=ObjectId(user_id)).delete()
        return jsonify({'status': 'success', 'message': 'Enemy removed'})


@user_bp.route('/<user_id>/friend-list', methods=['GET', 'POST', 'DELETE'])
def manage_friend_list(user_id):
    """Manage friend list"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    if request.method == 'GET':
        friends = FriendList.objects(user_id=ObjectId(user_id)).all()
        return jsonify({
            'friends': [{
                'id': str(f.id),
                'target_id': f.target_id,
                'target_username': f.target_username,
                'is_enabled': f.is_enabled
            } for f in friends]
        })
    
    data = request.get_json()
    
    if request.method == 'POST':
        target_id = data.get('target_id')
        target_username = data.get('target_username')
        
        friend = FriendList.objects(
            user_id=ObjectId(user_id),
            target_id=target_id
        ).first()
        
        if not friend:
            friend = FriendList(
                user_id=ObjectId(user_id),
                target_id=target_id,
                target_username=target_username,
                is_enabled=True
            )
            friend.save()
        else:
            friend.is_enabled = not friend.is_enabled
            friend.save()
        
        return jsonify({'status': 'success', 'message': 'Friend added/updated'})
    
    elif request.method == 'DELETE':
        friend_id = data.get('friend_id')
        FriendList.objects(id=ObjectId(friend_id), user_id=ObjectId(user_id)).delete()
        return jsonify({'status': 'success', 'message': 'Friend removed'})


@user_bp.route('/<user_id>/crush-list', methods=['GET', 'POST', 'DELETE'])
def manage_crush_list(user_id):
    """Manage crush list"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    if request.method == 'GET':
        crushes = CrushList.objects(user_id=ObjectId(user_id)).all()
        return jsonify({
            'crushes': [{
                'id': str(c.id),
                'target_id': c.target_id,
                'target_username': c.target_username,
                'is_enabled': c.is_enabled
            } for c in crushes]
        })
    
    data = request.get_json()
    
    if request.method == 'POST':
        target_id = data.get('target_id')
        target_username = data.get('target_username')
        
        crush = CrushList.objects(
            user_id=ObjectId(user_id),
            target_id=target_id
        ).first()
        
        if not crush:
            crush = CrushList(
                user_id=ObjectId(user_id),
                target_id=target_id,
                target_username=target_username,
                is_enabled=True
            )
            crush.save()
        else:
            crush.is_enabled = not crush.is_enabled
            crush.save()
        
        return jsonify({'status': 'success', 'message': 'Crush added/updated'})
    
    elif request.method == 'DELETE':
        crush_id = data.get('crush_id')
        CrushList.objects(id=ObjectId(crush_id), user_id=ObjectId(user_id)).delete()
        return jsonify({'status': 'success', 'message': 'Crush removed'})


@user_bp.route('/<user_id>/pv-lock', methods=['POST'])
def toggle_pv_lock(user_id):
    """Toggle private message lock"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    enabled = data.get('enabled', False)
    
    user.pv_lock_enabled = enabled
    user.save()
    
    return jsonify({
        'status': 'success',
        'message': f'PV lock {"enabled" if enabled else "disabled"}'
    })


@user_bp.route('/<user_id>/copy-profile', methods=['POST'])
def toggle_copy_profile(user_id):
    """Toggle profile copy feature"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    enabled = data.get('enabled', False)
    
    user.copy_profile_enabled = enabled
    user.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Copy profile {"enabled" if enabled else "disabled"}'
    })


@user_bp.route('/<user_id>/animations', methods=['POST'])
def toggle_animation_preset(user_id):
    """Toggle animation presets"""
    try:
        user = User.objects(id=ObjectId(user_id)).first()
    except:
        user = None
    
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    
    data = request.get_json()
    preset_name = data.get('preset_name')  # heart, love, oclock, star, snow
    enabled = data.get('enabled', False)
    
    preset = UserAnimationPreset.objects(
        user_id=ObjectId(user_id),
        preset_name=preset_name
    ).first()
    
    if not preset:
        preset = UserAnimationPreset(
            user_id=ObjectId(user_id),
            preset_name=preset_name,
            is_enabled=enabled
        )
        preset.save()
    else:
        preset.is_enabled = enabled
        preset.save()
    
    return jsonify({
        'status': 'success',
        'message': f'Animation preset {preset_name} {"enabled" if enabled else "disabled"}'
    })

# ============= SUBSCRIPTION CHANNEL ROUTES =============

@admin_bp.route('/subscription-channels', methods=['GET', 'POST'])
@admin_required
def manage_subscription_channels():
    """Manage mandatory subscription channels"""
    admin_id = ObjectId(session.get('admin_id'))
    
    if request.method == 'GET':
        channels = SubscriptionChannel.objects(admin_id=admin_id, is_active=True).all()
        return jsonify({
            'status': 'success',
            'channels': [{
                'id': str(c.id),
                'channel_id': c.channel_id,
                'channel_username': c.channel_username,
                'channel_title': c.channel_title,
                'is_active': c.is_active,
                'created_at': c.created_at.isoformat()
            } for c in channels]
        })
    
    # POST - Add new channel
    data = request.get_json()
    channel_id = data.get('channel_id')
    channel_username = data.get('channel_username')
    channel_title = data.get('channel_title')
    
    if not channel_id:
        return jsonify({'status': 'error', 'message': 'Channel ID required'}), 400
    
    # Check if already exists
    existing = SubscriptionChannel.objects(
        admin_id=admin_id,
        channel_id=channel_id
    ).first()
    
    if existing:
        return jsonify({'status': 'error', 'message': 'Channel already added'}), 400
    
    channel = SubscriptionChannel(
        admin_id=admin_id,
        channel_id=channel_id,
        channel_username=channel_username,
        channel_title=channel_title,
        is_active=True
    )
    channel.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Subscription channel added',
        'channel_id': str(channel.id)
    })


@admin_bp.route('/subscription-channels/<channel_id>', methods=['DELETE'])
@admin_required
def remove_subscription_channel(channel_id):
    """Remove subscription channel"""
    admin_id = ObjectId(session.get('admin_id'))
    
    try:
        channel = SubscriptionChannel.objects(
            id=ObjectId(channel_id),
            admin_id=admin_id
        ).first()
    except:
        channel = None
    
    if not channel:
        return jsonify({'status': 'error', 'message': 'Channel not found'}), 404
    
    channel.is_active = False
    channel.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Subscription channel removed'
    })


# ============= REPORT ROUTES =============

@admin_bp.route('/reports', methods=['GET', 'POST'])
@admin_required
def manage_reports():
    """Manage reports (spam/scam)"""
    admin_id = ObjectId(session.get('admin_id'))
    
    if request.method == 'GET':
        status = request.args.get('status', 'pending')
        reports = Report.objects(admin_id=admin_id, status=status).all()
        return jsonify({
            'status': 'success',
            'reports': [{
                'id': str(r.id),
                'target_id': r.target_id,
                'target_type': r.target_type,
                'target_username': r.target_username,
                'target_title': r.target_title,
                'reason': r.reason,
                'status': r.status,
                'notes': r.notes,
                'delete_request_sent': r.delete_request_sent,
                'created_at': r.created_at.isoformat(),
                'updated_at': r.updated_at.isoformat()
            } for r in reports]
        })
    
    # POST - Add new report
    data = request.get_json()
    target_id = data.get('target_id')
    target_type = data.get('target_type')  # channel, group, user
    target_username = data.get('target_username')
    target_title = data.get('target_title')
    reason = data.get('reason', 'spam')  # spam, scam, abuse, other
    
    if not target_id or not target_type:
        return jsonify({'status': 'error', 'message': 'Target ID and type required'}), 400
    
    # Check if already reported
    existing = Report.objects(
        admin_id=admin_id,
        target_id=target_id,
        status__in=['pending', 'reported']
    ).first()
    
    if existing:
        return jsonify({'status': 'error', 'message': 'Already reported'}), 400
    
    report = Report(
        admin_id=admin_id,
        target_id=target_id,
        target_type=target_type,
        target_username=target_username,
        target_title=target_title,
        reason=reason,
        status='pending'
    )
    report.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Report created',
        'report_id': str(report.id)
    })


@admin_bp.route('/report/<report_id>/skip', methods=['POST'])
@admin_required
def skip_report(report_id):
    """Skip report"""
    admin_id = ObjectId(session.get('admin_id'))
    
    try:
        report = Report.objects(
            id=ObjectId(report_id),
            admin_id=admin_id
        ).first()
    except:
        report = None
    
    if not report:
        return jsonify({'status': 'error', 'message': 'Report not found'}), 404
    
    report.status = 'skipped'
    report.updated_at = datetime.utcnow()
    report.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Report skipped'
    })


@admin_bp.route('/report/<report_id>/delete', methods=['POST'])
@admin_required
def delete_reported_content(report_id):
    """Mark as deleted"""
    admin_id = ObjectId(session.get('admin_id'))
    
    try:
        report = Report.objects(
            id=ObjectId(report_id),
            admin_id=admin_id
        ).first()
    except:
        report = None
    
    if not report:
        return jsonify({'status': 'error', 'message': 'Report not found'}), 404
    
    data = request.get_json() or {}
    notes = data.get('notes', 'Deleted')
    
    report.status = 'deleted'
    report.notes = notes
    report.updated_at = datetime.utcnow()
    report.save()
    
    return jsonify({
        'status': 'success',
        'message': 'Content marked as deleted'
    })


@admin_bp.route('/report/<report_id>/send-request', methods=['POST'])
@admin_required
def send_delete_request(report_id):
    """Send delete request to Telegram"""
    admin_id = ObjectId(session.get('admin_id'))
    
    try:
        report = Report.objects(
            id=ObjectId(report_id),
            admin_id=admin_id
        ).first()
    except:
        report = None
    
    if not report:
        return jsonify({'status': 'error', 'message': 'Report not found'}), 404
    
    data = request.get_json() or {}
    notes = data.get('notes', 'Delete request sent to Telegram')
    
    report.status = 'reported'
    report.delete_request_sent = True
    report.notes = notes
    report.updated_at = datetime.utcnow()
    report.save()
    
    # TODO: Integrate with Telegram API to send actual delete request
    # from telethon import TelegramClient
    # Send report to Telegram abuse team
    
    return jsonify({
        'status': 'success',
        'message': 'Delete request sent',
        'report_id': str(report.id)
    })


# Register blueprints with app
def register_blueprints(app):
    """Register all blueprints"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(payment_bp)