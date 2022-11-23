import pymysql
from src.routes.util.cfg import connectionDB

class db:
    def get_connection(self):
        return pymysql.connect(**connectionDB)

    def post_tagging(self, meta):
        with self.get_connection() as con:
            cur = con.cursor()

            ip = meta['ip']
            version = 1
            ua = meta['ua']
            source = meta['source']
            status = meta['status']
            time_global = meta['global_time']

            time_inference = meta['time_inference']
            result = meta['result']

            try:
                val = [ip]
                cur.execute("INSERT IGNORE INTO image_search.request_origen (request_ip) VALUES (%s)", val)
                con.commit()
            except:
                pass
            cur.execute(f'SELECT id_origen FROM image_search.request_origen WHERE request_ip = "{ip}"')
            ip_id = cur.fetchall()[0][0]

            val = [ip_id, version, ua, source, time_global, status]
            cur.execute(
                "INSERT INTO image_search.request_image (id_origen, id_version, request_useragent, request_source, request_datetime, request_globaltime, request_status) VALUES (%s, %s, %s, %s, NOW(), %s, %s)",
                val)

            id_request = con.insert_id()

            val = [id_request, time_inference, str(result)]
            cur.execute(
                "INSERT INTO image_search.tagging (id_request, tagging_time, tagging_result) VALUES (%s, %s, %s)",
                val)

            con.commit()

    def post_search(self, meta):
        with self.get_connection() as con:
            cur = con.cursor()

            ip = meta['ip']
            version = 1
            ua = meta['ua']
            source = meta['source']
            status = meta['status']
            time_global = meta['global_time']
            query = str(meta['query'])
            time_search = meta['time_search']
            time_embdeing = meta['time_embdeing']
            results = meta['results']

            try:
                val = [ip]
                cur.execute("INSERT IGNORE INTO image_search.request_origen (request_ip) VALUES (%s)", val)
                con.commit()
            except:
                pass
            cur.execute(f'SELECT id_origen FROM image_search.request_origen WHERE request_ip = "{ip}"')
            ip_id = cur.fetchall()[0][0]

            val = [ip_id, version, ua, source, time_global, status]
            cur.execute(
                "INSERT INTO image_search.request_image (id_origen, id_version, request_useragent, request_source, request_datetime, request_globaltime, request_status) VALUES (%s, %s, %s, %s, NOW(), %s, %s)",
                val)

            id_request = con.insert_id()

            val = [id_request, query, time_embdeing, time_search]
            cur.execute(
                "INSERT INTO image_search.search (id_request, search_image_query, search_time_embeding, search_time_qdrant) VALUES (%s, %s, %s, %s)",
                val)

            id_search = con.insert_id()

            getR = lambda x: [id_search, x['id_image'], x['id_source'], x['score'], x['status']]

            val = [getR(i) for i in results]

            # print(val)

            cur.executemany(
                'INSERT INTO image_search.search_result (id_search, id_image, id_source, result_score, result_status) VALUES (%s, %s, %s, %s, %s)',
                val)

            con.commit()
