import os
from app import create_app
from app.database import init_db

app = create_app()

# 🔥 IMPORTANT — database init yahi add karna hai
with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)