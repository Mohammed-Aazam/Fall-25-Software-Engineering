from moj import db
from moj.models import User, UserAction


def make_users():
	user = User(username='testuser', email='user@a.com', role='user')
	user.set_password('a')
	admin = User(username='admin', email='admin@a.com', role='admin')
	admin.set_password('a')
	return user, admin


def test_admin_can_edit_user_role(client, app):
	"""GIVEN a regular user and a logged-in admin_user
	WHEN the admin_user POSTs to /admin/edit_user/<user_id> with a new role and justification
	THEN the response is 200 after redirect and the user's role is changed in the DB
	"""
	with app.app_context():
		user, admin = make_users()
		db.session.add_all([user, admin])
		db.session.commit()
		user_id = user.id

	# login as admin
	client.post('/login', data={'username': 'admin', 'password': 'a'})

	response = client.post(f'/admin/edit_user/{user_id}', data={
		'role': 'admin',
		'justification': 'Promote for testing'
	}, follow_redirects=True)

	assert response.status_code == 200
	assert b'Admin Panel' in response.data

	with app.app_context():
		updated = User.query.get_or_404(user_id)
	assert updated.role == 'admin'

	# Ensure a UserAction audit entry was created with correct details
	with app.app_context():
		action = UserAction.query.filter_by(target_type='user', target_id=user_id).first()
		assert action is not None
		assert action.action_type == UserAction.ADMIN_EDIT_USER
		assert action.details == 'Promote for testing'
		# Verify the action was performed by the admin user
		admin_user = User.query.filter_by(username='admin').first()
		assert action.user_id == admin_user.id


def test_user_cannot_edit_user_role(client, app):
	"""GIVEN a regular user_A and a logged-in user_B
	WHEN user_B attempts to POST to /admin/edit_user/<user_A_id>
	THEN the response is 403 and user_A.role is not changed
	"""
	with app.app_context():
		user_a = User(username='alice', email='a@a.com', role='user')
		user_a.set_password('a')
		user_b = User(username='bob', email='b@b.com', role='user')
		user_b.set_password('a')
		db.session.add_all([user_a, user_b])
		db.session.commit()
		user_a_id = user_a.id

	# login as bob (regular user)
	client.post('/login', data={'username': 'bob', 'password': 'a'})

	response = client.post(f'/admin/edit_user/{user_a_id}', data={
		'role': 'admin',
		'justification': 'Attempted promotion'
	})

	assert response.status_code == 403

	with app.app_context():
		alice = User.query.get_or_404(user_a_id)
	assert alice.role == 'user'
