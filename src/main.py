import uvicorn

if __name__ == "__main__":
    uvicorn.run("codegen_api:app", host='0.0.0.0', port=5678, reload=True, debug=True)