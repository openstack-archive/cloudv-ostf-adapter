from pecan import hooks
from pecan import make_app
from cv_ostf_adapter import db


def setup_app(config):
    db.init_model()
    app_conf = dict(config.app)

    return make_app(
        app_conf.pop('root'),
        logging=getattr(config, 'logging', {}),
        hooks=[
            hooks.TransactionHook(
                db.start,
                db.start_read_only,
                db.commit,
                db.rollback,
                db.clear
            )
        ],
        **app_conf
    )
