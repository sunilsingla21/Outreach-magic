from app.extensions import mongo


def generate_looker_studio_url(view, *hosts):
    looker_studio_key = f'{view}LookerStudioBaseUrl'
    looker_studio_base_url: str = mongo.get_config(looker_studio_key)
    hosts_string = ','.join([h.crypt for h in hosts])
    looker_studio_url = looker_studio_base_url.format(hosts_string)
    return looker_studio_url
