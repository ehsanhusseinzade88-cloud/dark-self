from models import User, Payment, AdminSettings
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

class PaymentManager:
    """Manage user payments and gems"""
    
    @staticmethod
    def get_gem_price():
        """Get current gem price in Toman"""
        try:
            settings = AdminSettings.objects.first()
            if settings:
                return settings.gem_price_toman
        except:
            pass
        return 40  # Default price
    
    @staticmethod
    def create_payment_request(user_id, gem_amount):
        """Create a payment request from user"""
        gem_price = PaymentManager.get_gem_price()
        amount_toman = gem_amount * gem_price
        
        payment = Payment(
            user_id=user_id,
            gems=gem_amount,
            amount_toman=amount_toman,
            status='pending'
        )
        
        payment.save()
        
        return {
            'payment_id': str(payment.id),
            'gems': gem_amount,
            'amount_toman': amount_toman,
            'price_per_gem': gem_price,
            'status': 'pending'
        }
    
    @staticmethod
    def upload_receipt(payment_id, image_data):
        """Upload receipt image for payment"""
        try:
            from bson import ObjectId
            payment = Payment.objects(id=ObjectId(payment_id)).first()
        except:
            payment = None
            
        if not payment:
            return {'status': 'error', 'message': 'Payment not found'}
        
        payment.receipt_image = image_data
        payment.status = 'pending'
        payment.save()
        
        return {'status': 'success', 'message': 'Receipt uploaded successfully'}
    
    @staticmethod
    def approve_payment(payment_id, admin_id, note=''):
        """Approve payment and add gems to user"""
        try:
            from bson import ObjectId
            payment = Payment.objects(id=ObjectId(payment_id)).first()
        except:
            payment = None
            
        if not payment:
            return {'status': 'error', 'message': 'Payment not found'}
        
        user = User.objects(id=payment.user_id).first()
        if not user:
            return {'status': 'error', 'message': 'User not found'}
        
        # Add gems to user
        user.gems += payment.gems
        
        # Update payment
        payment.status = 'approved'
        payment.approved_by_admin = admin_id
        payment.approval_note = note
        payment.approved_at = datetime.utcnow()
        
        user.save()
        payment.save()
        
        return {
            'status': 'success',
            'message': f'Payment approved. User received {payment.gems} gems',
            'total_gems': user.gems
        }
    
    @staticmethod
    def reject_payment(payment_id, admin_id, note=''):
        """Reject payment"""
        try:
            from bson import ObjectId
            payment = Payment.objects(id=ObjectId(payment_id)).first()
        except:
            payment = None
            
        if not payment:
            return {'status': 'error', 'message': 'Payment not found'}
        
        payment.status = 'rejected'
        payment.approved_by_admin = admin_id
        payment.approval_note = note
        payment.approved_at = datetime.utcnow()
        
        payment.save()
        
        return {'status': 'success', 'message': 'Payment rejected successfully'}
    
    @staticmethod
    def get_pending_payments():
        """Get all pending payments"""
        try:
            payments = Payment.objects(status='pending').all()
            return [{
                'id': str(p.id),
                'user_id': p.user_id,
                'gems': p.gems,
                'amount_toman': p.amount_toman,
                'receipt_image': p.receipt_image,
                'created_at': p.created_at.isoformat()
            } for p in payments]
        except:
            return []
    
    @staticmethod
    def get_user_gems(user_id):
        """Get user's current gems"""
        try:
            user = User.objects(id=user_id).first()
            if user:
                return user.gems
        except:
            pass
        return 0


class GemDeductionScheduler:
    """Handle automatic gem deduction during self activation"""
    
    scheduler = BackgroundScheduler()
    
    @staticmethod
    def start_deduction_for_user(user_id, interval_seconds=3600):
        """Start gem deduction for a user (every hour by default)"""
        try:
            settings = AdminSettings.objects.first()
            gems_per_hour = settings.gems_per_hour if settings else 2
            
            # Schedule recurring job
            job_id = f'deduction_{user_id}'
            
            try:
                GemDeductionScheduler.scheduler.add_job(
                    GemDeductionScheduler.deduct_gems,
                    'interval',
                    seconds=interval_seconds,
                    args=[user_id, gems_per_hour],
                    id=job_id,
                    replace_existing=True
                )
                
                if not GemDeductionScheduler.scheduler.running:
                    GemDeductionScheduler.scheduler.start()
                
                return {'status': 'success', 'message': f'Deduction started for user {user_id}'}
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        except:
            return {'status': 'error', 'message': 'Error getting settings'}
    
    @staticmethod
    def stop_deduction_for_user(user_id):
        """Stop gem deduction for a user"""
        job_id = f'deduction_{user_id}'
        try:
            GemDeductionScheduler.scheduler.remove_job(job_id)
            
            # Deactivate self for this user
            user = User.objects(id=user_id).first()
            if user:
                user.time_enabled = False
                user.bio_time_enabled = False
                user.bio_date_enabled = False
                user.save()
            
            return {'status': 'success', 'message': f'Deduction stopped for user {user_id}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def deduct_gems(user_id, gems_count=2):
        """Deduct gems from user"""
        try:
            user = User.objects(id=user_id).first()
            if not user:
                GemDeductionScheduler.stop_deduction_for_user(user_id)
                return
            
            if user.gems >= gems_count:
                user.gems -= gems_count
                user.gems_spent += gems_count
                user.save()
            else:
                # Not enough gems - stop self
                GemDeductionScheduler.stop_deduction_for_user(user_id)
        except Exception as e:
            print(f"Error deducting gems: {e}")
    
    @staticmethod
    def check_minimum_gems(user_id):
        """Check if user has minimum gems to activate self"""
        try:
            settings = AdminSettings.objects.first()
            minimum_gems = settings.minimum_gems_activate if settings else 80
            
            user = User.objects(id=user_id).first()
            if not user:
                return {'status': 'error', 'has_minimum': False}
            
            has_minimum = user.gems >= minimum_gems
            return {
                'status': 'success',
                'has_minimum': has_minimum,
                'gems': user.gems,
                'required': minimum_gems,
                'remaining': max(0, minimum_gems - user.gems)
            }
        except:
            return {'status': 'error', 'has_minimum': False}

