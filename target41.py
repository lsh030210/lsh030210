import streamlit as st
import json
import os
from datetime import datetime

# 데이터 파일 경로 설정
DATA_FILE = "./goal_data.json"

# 데이터 불러오기
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
        else:
            data = {'tasks': {}, 'completed_tasks': [], 'goal': None}  # 초기 데이터 구조 설정
            save_data(data)
    except (FileNotFoundError, json.decoder.JSONDecodeError, TypeError):
        data = {'tasks': {}, 'completed_tasks': [], 'goal': None}  # 초기 데이터 구조 설정
        save_data(data)
    return data

# 데이터 저장하기
def save_data(data):
    try:
        with open(DATA_FILE, 'w') as file:
            json.dump(data, file, indent=4, default=str)  # default=str로 추가하여 datetime 등의 경우 처리
    except Exception as e:
        st.error(f"데이터 저장 중 오류가 발생했습니다: {str(e)}")

# 목표 설정하기
def set_goal(goal_text):
    data = load_data()
    data['goal'] = goal_text
    save_data(data)
    st.success(f"목표를 설정했습니다: {goal_text}")
    st.session_state.goal_set = True

# 임무 추가하기
def add_task(task_name, hardcore):
    data = load_data()
    if 'tasks' not in data:
        data['tasks'] = {}
    if 'completed_tasks' not in data:
        data['completed_tasks'] = []
    data['tasks'][task_name] = {'completed': False, 'hardcore': hardcore}
    save_data(data)
    st.success(f"{task_name} 임무가 추가되었습니다.")

# 임무 완료 처리하기
def complete_task(task_name):
    data = load_data()
    if 'tasks' not in data:
        data['tasks'] = {}
    if 'completed_tasks' not in data:
        data['completed_tasks'] = []
    if task_name in data['tasks']:
        if not data['tasks'][task_name]['completed']:
            data['tasks'][task_name]['completed'] = True
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data['completed_tasks'].append({'name': task_name, 'time': completion_time})
            save_data(data)
            if data['tasks'][task_name].get('hardcore', False):
                st.success(f"{task_name} 하드코어 임무를 완료했습니다! (+5 포인트)")
            else:
                st.success(f"{task_name} 임무를 완료했습니다! (+1 포인트)")

            check_goal_completion()  # 목표 달성 체크 함수 호출
        else:
            st.warning("이미 완료된 임무입니다.")
    else:
        st.error(f"{task_name} 임무를 찾을 수 없습니다.")

# 목표 달성 게이지 계산하기
def calculate_progress():
    data = load_data()
    if 'tasks' not in data:
        data['tasks'] = {}
    total_completed_tasks = sum(
        5 if data['tasks'][task].get('hardcore', False) and data['tasks'][task]['completed'] else 1
        if data['tasks'][task]['completed'] else 0
        for task in data['tasks']
    )
    return min(total_completed_tasks / 50, 1.0)

# 목표 달성 여부 체크하기
def check_goal_completion():
    progress_percent = calculate_progress() * 100
    if progress_percent >= 100:
        st.balloons()
        st.success("축하합니다! 모든 목표를 달성하셨습니다!")
        st.markdown("---")  # 이펙트를 구분하기 위한 줄 추가
        st.session_state.goal_completed = True

# 목표 설정이 필요한지 확인하기
def show_temporary_goal_set():
    if "goal_set" not in st.session_state:
        st.session_state.goal_set = False
    if "goal_completed" not in st.session_state:
        st.session_state.goal_completed = False

    data = load_data()
    current_goal = data.get('goal', None)

    if not st.session_state.goal_set and not st.session_state.goal_completed:
        if current_goal:
            st.write(f"현재 설정된 목표: **{current_goal}**")
        else:
            show_set_goal_form()

# 목표 설정 폼 표시하기
def show_set_goal_form():
    st.title("목표 설정")
    new_goal = st.text_input("새로운 목표를 입력하세요:")
    if st.button("목표 설정하기"):
        set_goal(new_goal)

# 임무 추가 페이지 표시하기
def show_add_task_page():
    st.title("임무 추가하기")
    task_name = st.text_input("추가할 임무 이름 입력:")
    hardcore = st.checkbox("Hardcore 임무 추가하기")

    if st.button("임무 추가"):
        add_task(task_name, hardcore)

# 임무 현황 페이지 표시하기
def show_task_status_page():
    st.title("임무 현황")
    data = load_data()
    if 'tasks' not in data:
        data['tasks'] = {}
    tasks_to_show = [task for task in data['tasks'] if not data['tasks'][task]['completed']]
    for task in tasks_to_show:
        col1, col2 = st.columns([4, 1])
        with col1:
            if data['tasks'][task].get('hardcore', False):
                st.markdown(f"- <span style='color:red;'>{task} (Hardcore)</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"- {task} (일반)")
        with col2:
            if st.button(f"임무 완료", key=task):
                complete_task(task)
                st.experimental_rerun()  # 임무 완료 후 페이지를 새로고침

# 완료된 임무 목록 페이지 표시하기
def show_completed_tasks_page():
    st.title("완료된 임무 목록")
    data = load_data()
    if 'completed_tasks' not in data:
        data['completed_tasks'] = []
    for task in data['completed_tasks']:
        task_name = task['name']
        completion_time = task['time']
        if data['tasks'][task_name].get('hardcore', False):
            st.markdown(f"- <span style='color:red;'>{task_name} (Hardcore) - <span style='color:white;'>{completion_time}</span></span>", unsafe_allow_html=True)
        else:
            st.markdown(f"- {task_name} (일반) - {completion_time}")

# 초기화 확인 페이지 표시하기
def show_reset_confirmation():
    if "reset_confirm" not in st.session_state:
        st.session_state.reset_confirm = False

    if st.button("목표 및 임무 초기화"):
        st.session_state.reset_confirm = True

    if st.session_state.reset_confirm:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("네, 초기화할래요."):
                reset_data()
                st.session_state.reset_confirm = False
                st.success("목표와 모든 임무가 초기화되었습니다.")
                st.experimental_rerun()  # 초기화 후 페이지를 새로고침
        with col2:
            if st.button("아니요, 초기화하지 않겠습니다."):
                st.session_state.reset_confirm = False
                st.experimental_rerun()  # 초기화를 취소하고 페이지를 새로고침

# 데이터 초기화하기
def reset_data():
    initial_data = {'tasks': {}, 'completed_tasks': [], 'goal': None}  # 초기 데이터 구조 설정
    save_data(initial_data)

# 메인 함수 실행하기
def main():
    st.sidebar.title("메뉴")
    pages = ["목표 달성 게이지", "임무 추가하기", "임무 현황", "완료된 임무 목록"]
    page = st.sidebar.radio("이동할 페이지 선택:", pages)

    show_temporary_goal_set()

    if page == "목표 달성 게이지":
        show_progress_page()
    elif page == "임무 추가하기":
        show_add_task_page()
    elif page == "임무 현황":
        show_task_status_page()
    elif page == "완료된 임무 목록":
        show_completed_tasks_page()

# 목표 달성 게이지 페이지 표시하기
def show_progress_page():
    st.title("목표 달성 게이지")

    progress_percent = calculate_progress() * 100
    st.progress(progress_percent / 100)  # 0에서 1 사이 값으로 변환하여 사용

    data = load_data()
    current_goal = data.get('goal', None)
    if current_goal:
        st.markdown(f"### 목표: **{current_goal}**")  # 크고 아름다운 글꼴로 목표 표시

    if progress_percent >= 100:
        st.balloons()
        st.success("축하합니다! 모든 목표를 달성하셨습니다!")
        st.markdown("---")  # 이펙트를 구분하기 위한 줄 추가

    show_reset_confirmation()

if __name__ == "__main__":
    main()
