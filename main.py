import simplejson as json
import psycopg2
import traceback
import decimal
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

def lambda_handler(event, context):
    # TODO implement
    print(event)
    try:
    
        #connect to the database
        connection = psycopg2.connect(user="pmok3",
                                  password="paydontwait",
                                  host="database117.ci9cgiakdb8y.us-east-2.rds.amazonaws.com",
                                  port="5432",
                                  database="paydontwaitdatabase")
        
        cursor = connection.cursor()
        
        #execute query and sanitize against SQL injection
        cursor.execute("create temporary view info as SELECT service_id, day_of_service, service_started FROM Service Where table_id = %s ORDER BY day_of_service DESC, service_started DESC LIMIT 1; create temporary view receipt as SELECT info.service_id as service_id, day_of_service, service_started, name as server, table_id, item_desc as description, quantity, price as amount FROM info NATURAL JOIN Service NATURAL JOIN Servers NATURAL JOIN Suborder NATURAL JOIN Items ORDER BY item_desc ASC; create temporary view total as SELECT sum(amount*quantity) as total FROM receipt; SELECT * FROM receipt, total; ",(event["queryStringParameters"]["table_id"],))
           
        receipt = cursor.fetchall()

        print(receipt)
        
        total = receipt[1][8]
        service_id, day_of_service, service_started, server, table_id = receipt[1][0:5]
        
        items = {}
        for i in range(1,len(receipt)):
            #items[description] = [quantity, amount]
            items[receipt[i][5]] = {"maxNumber": receipt[i][6], "cost": receipt[i][7], "number": receipt[i][6], "total": receipt[i][6]*receipt[i][7]}
            
        print(items)
        
        #close cursor, connection
        cursor.close()
        connection.close()
        
    
        return {
            'statusCode': 200,
            'headers': {
                "x-custom-header" : "my custom header value",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({"success": True, "total": total, "table_id": table_id, "service_id": service_id, "day_of_service": day_of_service, "service_started": service_started, "items": items}, cls=DateTimeEncoder)
        } 
    except Exception as err:
        print("Exception: " + str(err))
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {
                "x-custom-header" : "my custom header value",
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({"success": False, "error": "Exception"})
        }
        
    return {
        'statusCode': 500,
        'headers': {
            "x-custom-header" : "my custom header value",
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({"success": False, "error": "unknown"})
    }
