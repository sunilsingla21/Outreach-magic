import os

from flask import redirect, url_for
from flask_login import current_user


def is_user_verified():
    if not current_user.is_authenticated:
        return
    if current_user.verified:
        return
    return redirect(url_for('main.verify_wall'))


def is_user_approved():
    if not current_user.is_authenticated:
        return
    if current_user.approved:
        return
    return redirect(url_for('main.approve_wall'))


def create_app():
    from datetime import datetime
    from uuid import uuid4

    from flask import Flask, render_template
    from flask_login import current_user

    import app.models as models
    from app.config import Config
    from app.utils.files import svg

    app = Flask(__name__)

    app.config.from_object(Config)
    app.secret_key = app.config['SECRET_KEY']
    app.jinja_env.filters['zip'] = zip
    app.jinja_env.autoescape = True

    # Initialize Flask extensions
    from app.extensions import login_manager, minify, mongo, session

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    @login_manager.user_loader
    def load_user(id):
        return models.User.get_by_id(id)

    mongo.init_app(app)

    minify.init_app(app)

    app.config.update({'SESSION_MONGODB': mongo.cx})
    session.init_app(app)

    # Context injection and error handlers
    @app.context_processor
    def inject_data():
        from app.utils.constants import PAGES, PAGES_FOR_VIEW
        datetime_format = '%b %d %Y %H:%M:%S'
        date_format = '%b %d %Y'

        def format_date(date: datetime | None, only_date=False):
            if not date:
                return None
            return date.strftime(date_format if only_date else datetime_format)

        def unix_timestamp(date: datetime | None):
            if not date:
                return ''
            return date.timestamp()

        return dict(
            user=current_user,
            models=models,
            datetime_format=datetime_format,
            format_date=format_date,
            unix_timestamp=unix_timestamp,
            uuid=uuid4,
            svg=svg,
            local_env=os.getenv('LOCAL_ENV') == '1',
            pages=PAGES,
            pages_for_view=PAGES_FOR_VIEW,
        )

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('exceptions/400.html.j2'), 400

    @app.errorhandler(401)
    def not_authorized(e):
        return render_template('exceptions/401.html.j2'), 401

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('exceptions/404.html.j2'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('exceptions/500.html.j2'), 500

    # Register blueprints here
    from app.account import bp as account_bp
    from app.csv_upload import bp as csv_upload_bp
    from app.email_group import bp as email_group_bp
    from app.google import bp as google_bp
    from app.host import bp as host_bp
    from app.main import bp as main_bp
    from app.microsoft import bp as microsoft_bp
    from app.proxy_details import bp as proxy_details_bp
    from app.seed_batch import bp as seed_batch_bp
    from app.smartlead import bp as smartlead_bp
    from app.user import bp as user_bp
    from app.vps import bp as vps_bp
    from app.yahoo import bp as yahoo_bp

    require_verification_bps = [
        user_bp,
        host_bp,
        smartlead_bp,
        account_bp,
        csv_upload_bp,
        google_bp,
        microsoft_bp,
        seed_batch_bp,
        vps_bp,
        yahoo_bp,
        email_group_bp,
    ]
    for bp in require_verification_bps:
        bp.before_request(is_user_verified)
        bp.before_request(is_user_approved)

    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/u')
    app.register_blueprint(host_bp, url_prefix='/host')
    app.register_blueprint(smartlead_bp, url_prefix='/smartlead')
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(csv_upload_bp, url_prefix='/csv-upload')
    app.register_blueprint(seed_batch_bp, url_prefix='/seeds')
    app.register_blueprint(google_bp, url_prefix='/google')
    app.register_blueprint(microsoft_bp, url_prefix='/microsoft')
    app.register_blueprint(vps_bp, url_prefix='/vps')
    app.register_blueprint(yahoo_bp, url_prefix='/yahoo')
    app.register_blueprint(email_group_bp, url_prefix='/email-group')
    app.register_blueprint(proxy_details_bp, url_prefix='/proxy-details')

    return app
