from dateutil import parser as dateparser
import pymongo
import twitter
import logging

TWITTER_USERNAME = ''
TWITTER_PASSWORD = ''

logging.basicConfig(level=logging.DEBUG)

class TweetGetter(object):
    def __init__(self, options):
        super(TweetGetter, self).__init__()
        self.twitter_username = options.username
        self.db = pymongo.Connection().tweets
        self.db.statuses.create_index("id", unique=True)
        self.db.statuses.create_index([('user', pymongo.ASCENDING), ('id', pymongo.ASCENDING)])
        self.api = twitter.Api(username=TWITTER_USERNAME, password=TWITTER_PASSWORD)
        self.last_edge_id = None
        logging.debug("user=%s, db=%s, api=%s", self.twitter_username, self.db, self.api)

    def edge_existing_id_for_user(self, order=pymongo.ASCENDING):
        logging.debug("edge_existing_id_for_user: order=%s", order)
        try:
            edge_id = self.db.statuses.find({'user': self.twitter_username}).sort("id", order)[0]['id']
        except:
            logging.debug("edge_id is None")
            return None
        else:
            logging.debug("edge_id=%s", edge_id)
            return edge_id

    def fetch_statuses(self, max_id=None, since_id=None):
        opts = {'count': 200}
        if max_id:
            opts['max_id'] = max_id
        if since_id:
            opts['since_id'] = since_id
        logging.debug("fetch_statuses: opts=%s", opts)
        statuses = self.api.GetUserTimeline(self.twitter_username, **opts)
        logging.debug("twitter API: statuses=%s", [s.id for s in statuses])
        return statuses

    def fetch_and_store_statuses(self, **opts):
        statuses = self.fetch_statuses(**opts)
        if not statuses:
            logging.info("no more statuses")
        else:
            logging.debug("fetch_and_store_statuses: statuses: %s", [s.id for s in statuses])
        if statuses[0].id == opts.get('max_id'):
            statuses.pop(0)
        logging.debug("fetch_and_store_statuses: statuses to process: %s", [s.id for s in statuses])
        statuses_as_dicts = map(lambda s: {
            'id': s.id,
            'created_at': dateparser.parse(s.created_at),
            'favorited': s.favorited,
            'in_reply_to_screen_name': s.in_reply_to_screen_name,
            'in_reply_to_status_id': s.in_reply_to_status_id,
            'in_reply_to_user_id': s.in_reply_to_user_id,
            'source': s.source,
            'text': s.text,
            'truncated': s.truncated,
            'user': self.twitter_username,
        }, statuses)
        self.db.statuses.insert(statuses_as_dicts)

    def __fetch_and_store_all_statuses(self, order, id_name):
        edge_id = self.edge_existing_id_for_user(order)
        if edge_id:
            if order == pymongo.DESCENDING:
                message = "newer than status id=%s"
            else:
                message = "older than status id=%s"
            logging.info(message, edge_id)
            self.last_edge_id = edge_id
        opts = {id_name: edge_id}
        logging.debug("__fetch_and_store_all_statuses: opts=%s", opts)
        while True:
            try:
                self.fetch_and_store_statuses(**opts)
            except:
                break
            else:
                edge_id = self.edge_existing_id_for_user(order)
                if edge_id == self.last_edge_id:
                    logging.info("no more statuses to process")
                    break
                else:
                    self.last_edge_id = edge_id
                logging.debug("edge id=%s", edge_id)

    def fetch_and_store_all_statuses(self):
        if options.newer:
            order = pymongo.DESCENDING
            logging.debug("fetch_and_store_all_statuses: newer: order=%s", order)
            self.__fetch_and_store_all_statuses(order, 'since_id')
        else:
            order = pymongo.ASCENDING
            logging.debug("fetch_and_store_all_statuses: older: order=%s", order)
            self.__fetch_and_store_all_statuses(order, 'max_id')

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username",
                      help="Twitter username")
    parser.add_option("-n", "--newer", action="store_true", dest="newer", default=False,
                        help="Fetch tweets newer than what's in the database")
    (options, args) = parser.parse_args()
    if options.username is None or options.username == "":
        parser.error("Twitter username must be specified")

    getter = TweetGetter(options)
    getter.fetch_and_store_all_statuses()