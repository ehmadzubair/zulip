from zerver.lib.management import ZulipBaseCommand
import requests
from zerver.models import UserPresence

class Command(ZulipBaseCommand):
    help = 'Updates the user presence for the realm.'

    def add_arguments(self, parser):
        self.add_realm_args(parser=parser, required=True)
        parser.add_argument('-p', '--posturl', dest='post_url', type=str)

    def handle(self, *args, **options):
        post_url = options.get('post_url')
        realm_id = options.get('realm_id')
        self.stdout.write(self.style.SUCCESS('realm_id={realm_id}'.format(realm_id=realm_id)))
        self.stdout.write(self.style.SUCCESS('post_url={post_url}'.format(post_url=post_url)))

        presence_data = UserPresence.get_status_dict_by_realm(realm_id)

        # Add Logging

        resp = requests.post(post_url, json=presence_data)
        # Error Handling

        self.stdout.write(self.style.SUCCESS(resp.json()))



