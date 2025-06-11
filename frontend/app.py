import streamlit as st
import requests
import random

API_URL = "http://127.0.0.1:8001"

st.title("📖 Вивчення слів")

# Ініціалізація сесійного стану
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "words_to_update" not in st.session_state:
    st.session_state.words_to_update = []
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = "easy"
if "current_words" not in st.session_state:
    st.session_state.current_words = []
if "quiz_words" not in st.session_state:
    st.session_state.quiz_words = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "selected_answer" not in st.session_state:
    st.session_state.selected_answer = None
if "is_correct" not in st.session_state:
    st.session_state.is_correct = None
if "current_options" not in st.session_state:
    st.session_state.current_options = None
if "answered_questions" not in st.session_state:
    st.session_state.answered_questions = 0
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False

# 🔑 Вхід або реєстрація
if st.session_state.role is None:
    st.subheader("🔑 Вхід або реєстрація")

    tab1, tab2 = st.tabs(["🔓 Увійти", "🆕 Зареєструватися"])

    with tab1:
        username = st.text_input("Логін")
        password = st.text_input("Пароль", type="password")

        if st.button("Увійти"):
            if username and password:
                try:
                    login_data = {
                        "username": username,
                        "password": password
                    }
                    login_response = requests.post(f"{API_URL}/login/", json=login_data)
                    
                    if login_response.status_code == 200:
                        user_data = login_response.json()
                        st.session_state.username = username
                        st.session_state.user_id = user_data.get("user_id")
                        st.session_state.role = user_data.get("role")
                        st.success("✅ Успішний вхід!")
                        st.rerun()
                    else:
                        error_detail = login_response.json().get("detail", "Невідома помилка")
                        st.error(f"❌ {error_detail}")
                except Exception as e:
                    st.error(f"❌ Помилка входу: {str(e)}")
            else:
                st.warning("Будь ласка, введіть логін та пароль")

    with tab2:
        new_username = st.text_input("Новий логін")
        new_password = st.text_input("Новий пароль", type="password")

        if st.button("Зареєструватися"):
            if new_username and new_password:
                try:
                    register_data = {
                        "username": new_username,
                        "password": new_password
                    }
                    print(f"Sending registration request for user: {new_username}")  # Debug log
                    reg_response = requests.post(f"{API_URL}/register", json=register_data)
                    print(f"Registration response status: {reg_response.status_code}")  # Debug log
                    print(f"Registration response content: {reg_response.text}")  # Debug log
                    
                    if reg_response.status_code == 200:
                        st.success("✅ Реєстрація успішна! Тепер ви можете увійти в систему.")
                    else:
                        try:
                            error_detail = reg_response.json().get("detail", "Невідома помилка")
                            st.error(f"❌ {error_detail}")
                        except:
                            st.error(f"❌ Помилка сервера: {reg_response.text}")
                except Exception as e:
                    print(f"Registration error: {str(e)}")  # Debug log
                    st.error(f"❌ Помилка реєстрації: {str(e)}")
            else:
                st.warning("Будь ласка, введіть всі поля для реєстрації")

else:
    # 🔄 Вихід
    st.sidebar.button("🔄 Вийти", on_click=lambda: st.session_state.update(
        role=None, username=None, words_to_update=[], current_words=[], quiz_words=[], current_question=0, score=0, show_result=False, selected_answer=None, is_correct=None, current_options=None, quiz_completed=False
    ))

    # Створюємо вкладки для різних режимів
    tab1, tab2, tab3 = st.tabs(["📚 Вивчення слів", "🎯 Вікторина", "📊 Результати"])

    with tab1:
        # 📌 Додавання нового слова (Доступно тільки адміністратору)
        if st.session_state.role == "admin":
            st.subheader("📌 Додавання нового слова")
            new_word = st.text_input("Введіть слово")
            new_translation = st.text_input("Введіть переклад")
            new_difficulty = st.selectbox("Оберіть рівень складності", ["easy", "medium", "hard"], key="difficulty_add")

            if st.button("Додати слово"):
                add_word_response = requests.post(f"{API_URL}/words/add", json={
                    "word": new_word,
                    "translation": new_translation,
                    "difficulty": new_difficulty
                })
                if add_word_response.status_code == 200:
                    st.success("✅ Слово успішно додано!")
                else:
                    st.error(f"❌ Помилка додавання слова: {add_word_response.text}")

        # 📝 Вивчення слів
        st.subheader("📝 Вивчення слів")
        user_id = st.session_state.user_id
        
        # Вибір рівня складності
        difficulty = st.selectbox("Оберіть рівень складності", ["easy", "medium", "hard"], 
                                key="difficulty_learn",
                                index=["easy", "medium", "hard"].index(st.session_state.current_difficulty))
        
        if difficulty != st.session_state.current_difficulty:
            st.session_state.current_difficulty = difficulty
            st.session_state.current_words = []
            st.session_state.add_word_mode = False
            st.rerun()

        # Автоматичне завантаження слів для поточної групи
        if not st.session_state.current_words:
            response = requests.get(f"{API_URL}/words/{st.session_state.current_difficulty}")
            if response.status_code == 200:
                st.session_state.current_words = response.json()

        # Додати слово UI
        if "add_word_mode" not in st.session_state:
            st.session_state.add_word_mode = False
        if st.button("Додати слово"):
            st.session_state.add_word_mode = True
        if st.session_state.add_word_mode:
            new_word = st.text_input("Слово", key="add_word_input")
            new_translation = st.text_input("Переклад", key="add_translation_input")
            if st.button("Зберегти"):
                if new_word and new_translation:
                    add_word_response = requests.post(f"{API_URL}/words/add", json={
                        "word": new_word,
                        "translation": new_translation,
                        "difficulty": st.session_state.current_difficulty
                    })
                    if add_word_response.status_code == 200:
                        st.success("✅ Слово успішно додано!")
                        st.session_state.add_word_mode = False
                        # Refresh word list
                        response = requests.get(f"{API_URL}/words/{st.session_state.current_difficulty}")
                        if response.status_code == 200:
                            st.session_state.current_words = response.json()
                        st.rerun()
                    else:
                        st.error(f"❌ Помилка додавання слова: {add_word_response.text}")
                        st.session_state.add_word_mode = False
                        st.rerun()

        # Показ слів
        if st.session_state.current_words:
            # Fetch user progress for known words
            try:
                progress_response = requests.get(f"{API_URL}/progress/{user_id}")
                known_word_ids = set()
                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    known_word_ids = {p['word_id'] for p in progress_data if p.get('known')}
            except Exception:
                known_word_ids = set()
            for word in st.session_state.current_words:
                col1, col2 = st.columns([3, 1])
                with col1:
                    icon = " ✅" if word['id'] in known_word_ids else ""
                    st.write(f"**{word['word']}** - {word['translation']}{icon}")
                with col2:
                    if word['id'] in known_word_ids:
                        st.button("Знаю", key=f"know_{word['id']}", disabled=True)
                    else:
                        if st.button(f"Знаю", key=f"know_{word['id']}"):
                            st.session_state.words_to_update.append({
                                "user_id": user_id,
                                "word_id": word["id"],
                                "known": True
                            })
                            st.success(f"✅ Додано до списку: {word['word']}")

        # 📤 Групове збереження прогресу
        if st.session_state.words_to_update:
            if st.button("📤 Зберегти прогрес"):
                progress_response = requests.post(f"{API_URL}/progress/", json=st.session_state.words_to_update)
                if progress_response.status_code == 200:
                    st.success("✅ Всі слова збережені!")
                    st.session_state.words_to_update = []
                    st.rerun()
                else:
                    st.error(f"❌ Помилка збереження: {progress_response.text}")

        # 📊 Перевірка прогресу
        if st.button("Перевірити прогрес"):
            try:
                progress_response = requests.get(f"{API_URL}/progress/{user_id}")

                if progress_response.status_code == 200:
                    progress_data = progress_response.json()
                    if not progress_data:
                        st.warning("⚠️ Ви ще не вивчили жодного слова.")
                    else:
                        st.success("✅ Ваш прогрес:")
                        # Create a mapping from word_id to word/translation
                        word_map = {w['id']: w for w in st.session_state.current_words}
                        for progress in progress_data:
                            word = word_map.get(progress['word_id'])
                            if word:
                                st.write(f"Слово {word['word']} ({word['translation']}) - Вивчено ✅")
                            else:
                                st.write(f"Слово ID: {progress['word_id']} - Вивчено ✅")
                else:
                    st.error(f"❌ Помилка отримання прогресу: {progress_response.text}")

            except ValueError:
                st.error("❌ Неправильний ID користувача!")

    with tab2:
        st.header("🎯 Вікторина")
        
        # Ініціалізація змінних сесії
        if 'quiz_words' not in st.session_state:
            st.session_state.quiz_words = []
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'show_result' not in st.session_state:
            st.session_state.show_result = False
        if 'selected_answer' not in st.session_state:
            st.session_state.selected_answer = None
        if 'is_correct' not in st.session_state:
            st.session_state.is_correct = None
        if 'current_options' not in st.session_state:
            st.session_state.current_options = None
        if 'quiz_completed' not in st.session_state:
            st.session_state.quiz_completed = False
        
        # Вибір рівня складності
        difficulty = st.radio("Оберіть рівень складності:", ["easy", "medium", "hard"])
        
        if st.button("Почати вікторину"):
            # Отримуємо слова для вікторини
            response = requests.get(f"{API_URL}/words/{difficulty}")
            if response.status_code == 200:
                all_words = response.json()
                # Вибираємо 10 випадкових слів
                st.session_state.quiz_words = random.sample(all_words, min(10, len(all_words)))
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.show_result = False
                st.session_state.selected_answer = None
                st.session_state.is_correct = None
                st.session_state.current_options = None
                st.session_state.quiz_completed = False
                st.rerun()
            else:
                st.error("Помилка при завантаженні слів")
        
        # Відображення поточного питання
        if st.session_state.quiz_words and not st.session_state.quiz_completed:
            current_word = st.session_state.quiz_words[st.session_state.current_question]
            
            st.write(f"### Питання {st.session_state.current_question + 1} з {len(st.session_state.quiz_words)}")
            st.write(f"**Слово:** {current_word['word']}")
            
            # Створюємо варіанти відповідей
            if st.session_state.current_options is None:
                # Отримуємо всі можливі переклади
                all_translations = [w['translation'] for w in st.session_state.quiz_words]
                # Вибираємо правильну відповідь
                correct_answer = current_word['translation']
                # Вибираємо неправильні відповіді (виключаючи правильну)
                wrong_answers = [t for t in all_translations if t != correct_answer]
                # Беремо 3 випадкові неправильні відповіді
                wrong_answers = random.sample(wrong_answers, min(3, len(wrong_answers)))
                # Формуємо список всіх варіантів
                options = [correct_answer] + wrong_answers
                # Перемішуємо варіанти
                random.shuffle(options)
                st.session_state.current_options = options
            
            # Відображаємо варіанти відповідей
            selected_answer = st.radio(
                "Виберіть правильний переклад:",
                st.session_state.current_options,
                key=f"answer_{st.session_state.current_question}",
                disabled=st.session_state.show_result
            )
            
            if st.session_state.show_result:
                if st.session_state.is_correct:
                    st.success("✅ Правильно!")
                else:
                    st.error(f"❌ Неправильно. Правильна відповідь: {current_word['translation']}")
                
                if st.button("Наступне питання"):
                    st.session_state.current_question += 1
                    st.session_state.show_result = False
                    st.session_state.selected_answer = None
                    st.session_state.is_correct = None
                    st.session_state.current_options = None
                    # Перевіряємо чи це останнє питання
                    if st.session_state.current_question >= len(st.session_state.quiz_words):
                        st.session_state.quiz_completed = True
                        # Do NOT submit results or rerun here; handle in quiz_completed block
                    else:
                        st.rerun()
            else:
                if st.button("Перевірити відповідь"):
                    st.session_state.show_result = True
                    st.session_state.selected_answer = selected_answer
                    st.session_state.is_correct = selected_answer == current_word['translation']
                    if st.session_state.is_correct:
                        st.session_state.score += 1
                    st.rerun()
        
        # Відображення результатів після завершення вікторини
        if st.session_state.quiz_completed:
            st.success("🎉 Вікторину завершено!")
            st.write(f"### Ваш результат: {st.session_state.score}/{len(st.session_state.quiz_words)}")
            percentage = (st.session_state.score / len(st.session_state.quiz_words)) * 100
            st.write(f"Відсоток правильних відповідей: {percentage:.1f}%")
            # Зберігаємо результати вікторини лише якщо ще не збережено
            if not st.session_state.get('quiz_result_submitted', False):
                if st.session_state.user_id is None:
                    st.error("❌ Помилка: Не вдалося отримати ID користувача. Спробуйте перезайти в систему.")
                    if st.button("Перезайти в систему"):
                        st.session_state.clear()
                        st.rerun()
                else:
                    quiz_result = {
                        "user_id": st.session_state.user_id,
                        "total_questions": len(st.session_state.quiz_words),
                        "correct_answers": st.session_state.score,
                        "wrong_answers": len(st.session_state.quiz_words) - st.session_state.score
                    }
                    try:
                        response = requests.post(f"{API_URL}/quiz-results/", json=quiz_result)
                        if response.status_code == 200:
                            st.success("✅ Результати збережено!")
                            st.session_state.quiz_result_submitted = True
                        elif response.status_code == 404:
                            st.error("❌ Помилка: Користувача не знайдено. Спробуйте перезайти в систему.")
                            if st.button("Перезайти в систему"):
                                st.session_state.clear()
                                st.rerun()
                        else:
                            st.error(f"❌ Помилка збереження результатів: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Помилка збереження результатів: {str(e)}")
            if st.button("Почати нову вікторину"):
                st.session_state.quiz_words = []
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.show_result = False
                st.session_state.selected_answer = None
                st.session_state.is_correct = None
                st.session_state.current_options = None
                st.session_state.quiz_completed = False
                st.session_state.quiz_result_submitted = False
                st.rerun()

    with tab3:
        st.header("📊 Результати")
        
        if st.session_state.username:
            try:
                # Додаємо відлагоджувальну інформацію
                # st.write("Debug Information:")
                # st.write(f"Username: {st.session_state.get('username', 'Not set')}")
                # st.write(f"User ID: {st.session_state.get('user_id', 'Not set')}")
                # st.write(f"Role: {st.session_state.get('role', 'Not set')}")
                
                # Спочатку перевіряємо, чи існує користувач
                test_response = requests.get(f"{API_URL}/test-stats/{st.session_state.username}")
                st.write(f"Test response: {test_response.text}")
                
                if test_response.status_code == 200:
                    # Якщо користувач існує, отримуємо статистику
                    response = requests.get(f"{API_URL}/stats/{st.session_state.username}")
                    st.write(f"Stats response status: {response.status_code}")
                    # Remove or comment out the next line to avoid dumping all stats
                    # st.write(f"Stats response text: {response.text}")
                    
                    if response.status_code == 200:
                        stats = response.json()
                        # Only show the 10 most recent results
                        stats = sorted(stats, key=lambda x: x['date'], reverse=True)[:10]
                        st.write(f"Stats data: Showing {len(stats)} most recent results")
                        
                        if stats:
                            # Загальна статистика
                            total_quizzes = len(stats)
                            total_questions = sum(quiz["total_questions"] for quiz in stats)
                            total_correct = sum(quiz["correct_answers"] for quiz in stats)
                            total_wrong = sum(quiz["wrong_answers"] for quiz in stats)
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Всього вікторин", total_quizzes)
                            with col2:
                                st.metric("Всього питань", total_questions)
                            with col3:
                                st.metric("Правильних відповідей", total_correct)
                            with col4:
                                st.metric("Неправильних відповідей", total_wrong)
                            
                            # Відсоток правильних відповідей
                            if total_questions > 0:
                                correct_percentage = (total_correct / total_questions) * 100
                                st.progress(correct_percentage / 100)
                                st.write(f"Відсоток правильних відповідей: {correct_percentage:.1f}%")
                            
                            # Детальна статистика по кожній вікторині
                            st.subheader("Детальна статистика")
                            for i, quiz in enumerate(stats, 1):
                                with st.expander(f"Вікторина {i} від {quiz['date']}"):
                                    st.write(f"Загальна кількість питань: {quiz['total_questions']}")
                                    st.write(f"Правильних відповідей: {quiz['correct_answers']}")
                                    st.write(f"Неправильних відповідей: {quiz['wrong_answers']}")
                                    if quiz['total_questions'] > 0:
                                        quiz_percentage = (quiz['correct_answers'] / quiz['total_questions']) * 100
                                        st.progress(quiz_percentage / 100)
                                        st.write(f"Відсоток правильних відповідей: {quiz_percentage:.1f}%")
                        else:
                            st.info("👋 Вітаємо! Почніть вікторину, щоб побачити свої результати.")
                    else:
                        st.error(f"❌ Помилка отримання статистики: {response.text}")
                else:
                    st.error(f"❌ Помилка перевірки користувача: {test_response.text}")
            except Exception as e:
                st.error(f"❌ Помилка: {str(e)}")
        else:
            st.warning("⚠️ Будь ласка, увійдіть в систему для перегляду результатів")
