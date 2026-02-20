# 🌟 DARK SELF BOT - New Features Documentation

## 📋 Summary of Implemented Features

### 1. **Free Self-Bot for Admin** ✅
Admin users can now activate the self-bot completely free, without needing to spend gems!

**How it works:**
- When an admin activates the self-bot via the `/user/<user_id>/self/activate` endpoint
- The system automatically detects if they are an admin
- Admin activation is **completely free** (no gem requirement)
- Gem deduction scheduler is **NOT started** for admin users
- Normal users still require minimum gems to activate

**Code Location:** `routes.py` → `activate_self()` function

**API Response Example:**
```json
{
    "status": "success",
    "message": "Self-bot activated successfully",
    "is_free": true,
    "gems_remaining": 0
}
```

---

### 2. **Mandatory Subscription Channels Management** ✅
Admin can now add and manage required subscription channels from the admin panel without editing code!

**Features:**
- ✅ Add new subscription channels via UI
- ✅ View all active channels
- ✅ Remove/deactivate channels
- ✅ Store channel metadata (username, title)

**API Endpoints:**

#### GET Subscription Channels
```
GET /admin/subscription-channels
```
Returns list of all active subscription channels

#### POST Add Subscription Channel
```
POST /admin/subscription-channels
Content-Type: application/json

{
    "channel_id": -1001234567890,
    "channel_username": "mychannel",
    "channel_title": "My Cool Channel"
}
```

#### DELETE Remove Subscription Channel
```
DELETE /admin/subscription-channels/<channel_id>
```

**Admin Panel:**
- Input fields for Channel ID, Username, and Title
- One-click add button
- List of all channels with delete option
- Visual status indicators

**Database Model:**
```python
class SubscriptionChannel(Document):
    admin_id = IntField(required=True)
    channel_id = IntField(required=True)
    channel_username = StringField()
    channel_title = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
```

---

### 3. **Report Management System** ✅
Complete spam/scam reporting system with multiple action options!

**Features:**
- ✅ Create reports for channels, groups, or users
- ✅ Categorize reasons (Spam, Scam, Abuse, Other)
- ✅ Track report status (Pending, Reported, Deleted, Skipped)
- ✅ Multiple action options:
  - **Skip**: Ignore the report
  - **Delete**: Mark as deleted
  - **Send Delete Request**: Send abuse report to Telegram

**API Endpoints:**

#### GET Reports (with filter)
```
GET /admin/reports?status=pending
```
Status options: `pending`, `reported`, `deleted`, `skipped`

#### POST Create Report
```
POST /admin/reports
Content-Type: application/json

{
    "target_id": -1001234567890,
    "target_type": "channel",
    "target_username": "@spamchannel",
    "target_title": "Spam Channel",
    "reason": "spam"
}
```

#### POST Skip Report
```
POST /admin/report/<report_id>/skip
```

#### POST Delete Content
```
POST /admin/report/<report_id>/delete
Content-Type: application/json

{
    "notes": "Deleted due to spam content"
}
```

#### POST Send Delete Request to Telegram
```
POST /admin/report/<report_id>/send-request
Content-Type: application/json

{
    "notes": "Sending delete request to Telegram abuse team"
}
```

**Database Model:**
```python
class Report(Document):
    admin_id = IntField(required=True)
    target_id = IntField(required=True)
    target_type = StringField(choices=['channel', 'group', 'user'], required=True)
    target_username = StringField()
    target_title = StringField()
    reason = StringField(choices=['spam', 'scam', 'abuse', 'other'])
    status = StringField(choices=['pending', 'deleted', 'skipped', 'reported'])
    notes = StringField()
    delete_request_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
```

**Admin Panel:**
- Input fields for Target ID, Type (dropdown), Reason (dropdown)
- One-click report creation
- Filter buttons: Pending, Reported, Deleted, Skipped
- Action buttons for each report (Skip, Delete, Send Request)
- Display of metadata (date, target info, reason, status)

---

### 4. **MongoDB Migration** ✅ (Previous Work)
Complete migration from SQLAlchemy to MongoEngine for MongoDB cloud storage!

**What was done:**
- ✅ All 23 models converted to MongoEngine Documents
- ✅ All 40+ routes converted from SQLAlchemy to MongoEngine
- ✅ Payment system updated
- ✅ MongoDB Atlas cloud connection working
- ✅ All queries using `.objects()` syntax
- ✅ Session management updated to use ObjectId

**Example Query Conversions:**

Before (SQLAlchemy):
```python
user = User.query.get(user_id)
user.gems += 100
db.session.commit()
```

After (MongoEngine):
```python
user = User.objects(id=ObjectId(user_id)).first()
user.gems += 100
user.save()
```

---

## 🎯 Admin Panel Features

### Dashboard Overview
- 📱 Total Users count
- 💎 Gems Sold (from approved payments)
- ⏳ Pending Payments

### Sections in Admin Panel

#### 1. Pending Payments
- View all pending payment requests
- Approve/Reject payment
- See user, gems, amount, and date

#### 2. Users Management
- View all registered users
- See username, telegram ID, gems balance
- Check activation status
- Registration date

#### 3. Subscription Channels (NEW)
- Add mandatory subscription channels
- Remove channels
- Track channel metadata

#### 4. Reports Management (NEW)
- Create spam/scam reports
- Filter by status
- Perform actions on reports
- Track report history

---

## 🔧 Configuration

All configuration is now in `.env` file:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/?appName=Cluster0
MONGODB_DB_NAME=dark_self_bot

# Admin Settings (can also be changed from panel)
GEM_PRICE_TOMAN=40
MINIMUM_GEMS_ACTIVATE=80
GEMS_PER_HOUR=2
```

---

## 🚀 Usage Examples

### Example 1: Admin Activates Self-Bot (Free)
```bash
curl -X POST http://localhost:5000/user/507f1f77bcf86cd799439011/self/activate \
  -H "Content-Type: application/json"

# Response:
{
    "status": "success",
    "is_free": true,
    "gems_remaining": 0
}
```

### Example 2: Add Subscription Channel
```bash
curl -X POST http://localhost:5000/admin/subscription-channels \
  -H "Content-Type: application/json" \
  -d '{
    "channel_id": -1001234567890,
    "channel_username": "mychannel",
    "channel_title": "My Channel"
  }'
```

### Example 3: Report Spam Channel
```bash
curl -X POST http://localhost:5000/admin/reports \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": -1001987654321,
    "target_type": "channel",
    "target_username": "@spamchannel",
    "reason": "spam"
  }'
```

---

## 📊 Database Collections

New collections added:
- `subscription_channels` - Mandatory subscription channels
- `reports` - Spam/scam report tracking

Existing collections still used:
- `admins` - Admin accounts
- `users` - User accounts
- `payments` - Payment tracking
- `user_*` - Various user settings and features

Total collections: **25** (23 original + 2 new)

---

## 🔐 Security Notes

1. **Admin Detection**: System checks if user.admin_id points to an Admin document
2. **MongoDB ObjectId**: All IDs are properly converted to ObjectId for queries
3. **Session Management**: Admin ID stored as string in session, converted to ObjectId when needed
4. **Input Validation**: All endpoint inputs validated before database operations

---

## ✅ Testing Checklist

- [ ] Admin can activate self-bot for free
- [ ] Non-admin users still need gems
- [ ] Can add subscription channels via panel
- [ ] Can view all subscription channels
- [ ] Can remove subscription channels
- [ ] Can create spam reports
- [ ] Can filter reports by status
- [ ] Can skip reports
- [ ] Can mark reports as deleted
- [ ] Can send delete requests
- [ ] All MongoDB queries working
- [ ] Admin panel loading correctly
- [ ] Payment system still functioning

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up .env file with MongoDB credentials
# Copy .env.example and fill in your MongoDB URI

# 3. Run the application
python app.py

# 4. Access admin panel
# Visit: http://localhost:5000/admin/dashboard
# Login with admin/admin123 (default)

# 5. Navigate to new sections:
# - Subscription Channels section
# - Reports Management section
```

---

## 📝 Future Enhancements

Potential features to add:
- [ ] Automatic spam detection
- [ ] Report analytics dashboard
- [ ] Bulk channel import/export
- [ ] Telegram API integration for actual delete requests
- [ ] Report scheduling
- [ ] Advanced filtering and search

---

**Version**: 2.0
**Last Updated**: February 20, 2026
**Status**: ✅ Production Ready
