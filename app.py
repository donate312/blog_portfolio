from website import create_app
from flask_wtf.csrf import CSRFProtect

app = create_app()

# Set a secret key for CSRF protection
app.config['SECRET_KEY'] = 'DmO138252'

csrf = CSRFProtect(app)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000 )
    
