# Server Specific Configurations
server = {
    'port': '8080',
    'host': '0.0.0.0'
}

# Pecan Application Configurations
app = {
    'root': 'cloudv_ostf_adapter._adapter_app.controllers.root.RootController',
    'modules': ['cloudv_ostf_adapter._adapter_app'],
    'static_root': '%(confdir)s/../../public',
    'template_path': '%(confdir)s/../templates',
    'debug': True,
    'errors': {
        '404': '/error/404',
        '__force_dict__': True
    }
}

sqlalchemy = {
    'url': 'sqlite:///:memory:'
}

# Custom Configurations must be in Python dictionary format::
#
# foo = {'bar':'baz'}
#
# All configurations are accessible at::
# pecan.conf
