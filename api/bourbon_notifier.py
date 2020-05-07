from bottle import Bottle, request

from ohlq import main

@app.get('/api')
def api():
    domain = request.query.get('domain')
    result = main()
    return dict(data=result)