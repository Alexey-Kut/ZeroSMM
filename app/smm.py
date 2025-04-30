from flask import Blueprint, render_template, request, flash, session, redirect, url_for, jsonify
from app.models import User
from app import db
from generators.text_gen import PostGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from social_stats.vk_stats import VKStats
from config import openai_key
from app.forms import PostForm

smm_bp = Blueprint('smm', __name__)

# ✅ Панель управления
@smm_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

# ✅ Форма для генерации
@smm_bp.route('/post-generator', methods=['GET'])
def post_generator():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    form = PostForm()
    return render_template('post_generator.html', form=form)

# ✅ Результаты генерации
@smm_bp.route('/generate-result', methods=['POST'])
def generate_result():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    form = PostForm(request.form)  # 🛠 Передаем данные из формы
    post_content = None
    image_url = None

    if form.validate_on_submit():
        tone = form.tone.data.strip()
        topic = form.topic.data.strip()
        generate_image = form.generate_image.data

        if not tone or not topic:
            flash('Пожалуйста, заполните все поля!', 'danger')
            return redirect(url_for('smm.post_generator'))

        try:
            post_gen = PostGenerator(openai_key, tone, topic)
            post_content = post_gen.generate_post()
        except Exception as e:
            flash(f'Ошибка при генерации поста: {str(e)}', 'danger')

        if generate_image:
            try:
                image_gen = ImageGenerator(openai_key)
                image_prompt = post_gen.generate_post_image_description()
                image_url = image_gen.generate_image(image_prompt)
            except Exception as e:
                flash(f'Ошибка при генерации изображения: {str(e)}', 'danger')

    return render_template('generated_result.html', form=form, post_content=post_content, image_url=image_url)

# ✅ Повторная генерация текста
@smm_bp.route('/regenerate-text', methods=['POST'])
def regenerate_text():
    data = request.get_json()
    tone = data.get('tone', 'нейтральный')
    topic = data.get('topic', 'Без темы')

    try:
        post_gen = PostGenerator(openai_key, tone, topic)
        new_text = post_gen.generate_post()
        return jsonify({"new_text": new_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Повторная генерация изображения
@smm_bp.route('/regenerate-image', methods=['POST'])
def regenerate_image():
    data = request.get_json()
    topic = data.get('topic', 'Без темы')

    try:
        image_gen = ImageGenerator(openai_key)
        image_prompt = f"Создай изображение на тему: {topic}"
        new_image_url = image_gen.generate_image(image_prompt)
        return jsonify({"new_image_url": new_image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Публикация в VK
@smm_bp.route('/publish-to-vk', methods=['POST'])
def publish_to_vk():
    if 'user_id' not in session:
        return jsonify({"error": "Необходимо войти в систему"}), 403

    user = User.query.get(session['user_id'])

    if not user.vk_api_id or not user.vk_group_id:
        return jsonify({"error": "Не указаны VK API ID и Group ID"}), 400

    data = request.get_json()
    content = data.get('content')
    image_url = data.get('image_url')

    try:
        vk_publisher = VKPublisher(user.vk_api_id, user.vk_group_id)
        vk_publisher.publish_post(content, image_url)
        return jsonify({"message": "Пост опубликован в VK"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Настройки VK API
@smm_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.vk_api_id = request.form.get('vk_api_id', '').strip()
        user.vk_group_id = request.form.get('vk_group_id', '').strip()

        if not user.vk_api_id or not user.vk_group_id:
            flash('VK API ID и Group ID не могут быть пустыми!', 'danger')
        else:
            db.session.commit()
            flash('Настройки сохранены!', 'success')

    return render_template('settings.html', user=user)

# ✅ Статистика VK
@smm_bp.route('/vk-stats', methods=['GET'])
def vk_stats():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if not user.vk_api_id or not user.vk_group_id:
        flash('Вы не указали VK API ID или Group ID в настройках!', 'danger')
        return redirect(url_for('smm.settings'))

    try:
        vk_stats = VKStats(user.vk_api_id, user.vk_group_id)
        followers_count = vk_stats.get_followers()

        stats = {
            "Подписчики": followers_count,
            "Лайки": "N/A",
            "Комментарии": "N/A",
            "Репосты": "N/A"
        }
    except Exception as e:
        flash(f'Ошибка при получении статистики: {str(e)}', 'danger')
        stats = {}

    return render_template('vk_stats.html', stats=stats)
