from fastapi import FastAPI
app=FastAPI(title='KKM OPTIMA REGISTER')
@app.get('/health')
def health(): return {'status':'ok'}
