from logging import debug
from Website import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True) #debug for if we change the code this would rerun the server