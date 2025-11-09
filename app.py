from flask import Flask, request, jsonify, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from models import db
from datetime import timedelta
from xss import detect_xss
import os 

app = Flask(__name__)

# CORS

CORS(app, resources={r"/*": {"origins": "*"}})

# Konfigurasi

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "Super-secret-key"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 # 2MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Init

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

# Routes Beserta Controller

@app.route('/')
def index():
    return "Service is Online!"

# Route Uploads
@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------ BAGIAN USER ------------------
from models import User

# Register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username and not password:
        return jsonify({"message": "Mohon masukkan seluruh field!"}), 422
    
    if not username:
        return jsonify({"message": "Mohon masukkan field username!"}), 422
    if not password:
        return jsonify({"message": "Mohon masukkan field password!"}), 422
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Maaf username telah diambil!"}), 400
    
    newUser = User()
    newUser.username = username
    newUser.set_password(password)

    db.session.add(newUser)
    db.session.commit()

    return jsonify({"message": "Berhasil!"}), 201

# Login
@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username and not password:
        return jsonify({"message": "Mohon masukkan seluruh field!"}), 422
    
    if not username:
        return jsonify({"message": "Mohon masukkan field username!"}), 422
    if not password:
        return jsonify({"message": "Mohon masukkan field password!"}), 422
    
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        accessToken = create_access_token(identity=str(user.id))
        return jsonify({"message": "Berhasil!", "access_token": accessToken}), 200
    else:
        return jsonify({"message": "Invalid credentials!"}), 401
    
# ------------------ BAGIAN PRODUK ------------------
import uuid
from models import Produk

@app.route('/produk', methods=['GET'])
def produk_list():
    produk = Produk.query.all()
    data = []
    
    for p in produk:
        data.append({
            'id': p.id,
            'nama': p.nama,
            'deskripsi': p.deskripsi,
            'harga': p.harga,
            'gambar': request.host_url + os.path.join(app.config['UPLOAD_FOLDER'], p.gambar)
        })
    
    return jsonify({"message": "Berhasil!", "data": data}), 200

@app.route('/produk/<int:id>', methods=['GET'])
def get_by_id_produk(id):
    produk = Produk.query.filter_by(id=id).first()

    if not produk:
        return jsonify({"message": "Produk tidak ditemukan!"}), 404
    
    data = {
        'id': produk.id,
        'nama': produk.nama,
        'deskripsi': produk.deskripsi,
        'hagra': produk.harga,
        'gambar': request.host_url + os.path.join(app.config['UPLOAD_FOLDER'], produk.gambar)
    }

    return jsonify({"message": "Berhasil!", 'data': data}), 200

@app.route('/produk/create', methods=['POST'])
@jwt_required()
def create_produk():
    nama = request.form.get('nama')
    deskripsi = request.form.get('deskripsi')
    harga = request.form.get('harga')
    gambar = request.files.get('gambar')

    if not all([nama, deskripsi, harga, gambar]):
        return jsonify({'message': "Mohon masukkan seluruh field termasuk gambar!"}), 422
    
    # Validasi tipe file

    allowed_ext = {'png', 'jpg', 'jpeg', 'webp'}
    filename = gambar.filename.lower()

    if not ('.' in filename and filename.rsplit('.', 1)[1] in allowed_ext):
        return jsonify({'message': 'Format gambar tidak didukung!'}), 415
    
    ext = filename.rsplit('.', 1)[1]
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    gambar.save(file_path)

    try:
        new_produk = Produk()
        new_produk.nama = nama
        new_produk.deskripsi = deskripsi
        new_produk.harga = harga
        new_produk.gambar = new_filename

        db.session.add(new_produk)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan!", 'error': str(e)}), 500
    
    return jsonify({'message': "Berhasil!", 'data': {
        'id': new_produk.id,
        'nama': new_produk.nama,
        'deskripsi': new_produk.deskripsi,
        'harga': new_produk.harga,
        'gambar': request.host_url + os.path.join(app.config['UPLOAD_FOLDER'], new_produk.gambar)
    }}), 201

@app.route('/produk/update', methods=['POST'])
def update_produk():
    id = request.form.get('id')
    nama = request.form.get('nama')
    deskripsi = request.form.get('deskripsi')
    harga = request.form.get('harga')
    gambar = request.files.get('gambar')

    produk = Produk.query.filter_by(id=id).first()

    if not produk:
        return jsonify({'message': "Produk tidak ditemukan!"}), 404
    
    if nama:
        produk.nama = nama
    if deskripsi:
        produk.deskripsi = deskripsi
    if harga:
        produk.harga = harga

    if gambar:
        allowed_ext = {'png', 'jpg', 'jpeg', 'webp'}
        filename = gambar.filename.lower()

        if not ('.' in filename and filename.rsplit('.', 1)[1] in allowed_ext):
            return jsonify({'message': 'Format gambar tidak didukung!'}), 415

        ext = filename.rsplit('.', 1)[1]
        new_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        gambar.save(file_path)

        old_path = os.path.join(app.config['UPLOAD_FOLDER'], produk.gambar)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                print(f"Gagal menghapus gambar lama: {e}")

        produk.gambar = new_filename

    try:
        db.session.commit()
    except Exception as e:
        return jsonify({'message': "Terjadi kesalahan saat update!", 'error': str(e)}), 500

    return jsonify({
        'message': "Produk berhasil diupdate!",
        'data': {
            'id': produk.id,
            'nama': produk.nama,
            'deskripsi': produk.deskripsi,
            'harga': produk.harga,
            'gambar': request.host_url + os.path.join(app.config['UPLOAD_FOLDER'], produk.gambar)
        }
    }), 200

@app.route('/produk/<int:id>', methods=['DELETE'])
def delete_by_id_produk(id):
    produk = Produk.query.filter_by(id=id).first()

    if not produk:
        return jsonify({"message": "Produk tidak ditemukan!"}), 404
    
    old_path = os.path.join(app.config['UPLOAD_FOLDER'], produk.gambar)
    if os.path.exists(old_path):
        try:
            os.remove(old_path)
        except Exception as e:
            print(f"Gagal menghapus gambar: {e}")
        
    try:
        db.session.delete(produk)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan saat menghapus produk!", "error": str(e)}), 500

    return jsonify({"message": "Produk berhasil dihapus!"}), 200

# ------------------ BAGIAN TESTIMONI ------------------
from models import Testimoni

@app.route('/testimoni', methods=['GET'])
def get_all_testimoni():
    testimoni = Testimoni.query.order_by(Testimoni.id.desc()).all()
    data = []

    for t in testimoni:
        data.append({
            'id': t.id,
            'nama': t.nama,
            'deskripsi': t.deskripsi,
            'rating': t.rating,
            'created_at': t.created_at.isoformat() if t.created_at else None
        })

    return jsonify({"message": "Berhasil!", "data": data}), 200


@app.route('/testimoni/create', methods=['POST'])
def create_testimoni():
    data = request.get_json()
    nama = data.get('nama')
    deskripsi = data.get('deskripsi')
    rating = data.get('rating')

    if not all([nama, deskripsi, rating]):
        return jsonify({"message": "Mohon masukkan seluruh field (nama, deskripsi, rating)!"}), 422

    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            return jsonify({"message": "Rating harus antara 1 sampai 5!"}), 422
    except ValueError:
        return jsonify({"message": "Rating harus berupa angka!"}), 422

    for field_name, value in {"nama": nama, "deskripsi": deskripsi}.items():
        if detect_xss(value):
            return jsonify({"message": f"Input pada field '{field_name}' terdeteksi mengandung yang invalid!"}), 400

    try:
        new_testimoni = Testimoni(
            nama=nama,
            deskripsi=deskripsi,
            rating=rating
        )
        db.session.add(new_testimoni)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan!", "error": str(e)}), 500

    return jsonify({
        "message": "Berhasil!",
        "data": {
            "id": new_testimoni.id,
            "nama": new_testimoni.nama,
            "deskripsi": new_testimoni.deskripsi,
            "rating": new_testimoni.rating,
            "created_at": new_testimoni.created_at.isoformat() if new_testimoni.created_at else None
        }
    }), 201


@app.route('/testimoni/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_testimoni(id):
    testimoni = Testimoni.query.filter_by(id=id).first()

    if not testimoni:
        return jsonify({"message": "Testimoni tidak ditemukan!"}), 404

    try:
        db.session.delete(testimoni)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": "Terjadi kesalahan saat menghapus testimoni!", "error": str(e)}), 500

    return jsonify({"message": "Testimoni berhasil dihapus!"}), 200
