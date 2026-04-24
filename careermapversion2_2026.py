import streamlit as st

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(page_title="Career Pathfinder", layout="centered")

# ----------------------------
# Data
# ----------------------------
CATEGORIES = ["analytical", "creative", "social", "practical", "entrepreneurial", "athlete"]

CATEGORY_INFO = {
    "analytical": {
        "label": "Analytical",
        "desc": "You like problem-solving, logic, and figuring out how things work."
    },
    "creative": {
        "label": "Creative",
        "desc": "You enjoy designing, writing, imagining, and building original ideas."
    },
    "social": {
        "label": "Social",
        "desc": "You like working with people, helping, teaching, and communicating."
    },
    "practical": {
        "label": "Practical",
        "desc": "You enjoy hands-on work, building, fixing, and using tools/tech."
    },
    "entrepreneurial": {
        "label": "Entrepreneurial",
        "desc": "You like leading, taking initiative, and creating opportunities."
    },
    "athlete": {
        "label": "Athletic",
        "desc": "You enjoy physical performance, training, sports, and movement."
    },
}

CAREER_OPTIONS = {
    “analytical”: [“Software Developer”, “Data Scientist”, “Engineer”, “Research Scientist”, “Cybersecurity Analyst”],
    “creative”: [“Graphic Designer”, “Writer”, “Filmmaker”, “UI/UX Designer”, “Game Designer”],
    “social”: [“Psychologist”, “Teacher”, “Social Worker”, “Counselor”, “Nurse”],
    “practical”: [“Mechanical Engineer”, “Electrician”, “Technician”, “Carpenter”, “Automotive Technician”],
    “entrepreneurial”: [“Entrepreneur”, “Business Manager”, “Startup Founder”, “Marketing Specialist”, “Product Manager”],
    “athlete”: [“Fitness Instructor”, “Physical Therapist”, “Coach”, “Sports Trainer”, “Athletic Director”]
}

# Maps each career to recommended college majors + key high school prep courses
CAREER_ROADMAP = {
    “Software Developer”: {
        “majors”: [“Computer Science”, “Software Engineering”, “Computer Engineering”],
        “hs_prep”: [“AP Computer Science”, “AP Calculus”, “Statistics”],
        “alt_paths”: [“Community college → transfer”, “Coding bootcamp + portfolio”],
    },
    “Data Scientist”: {
        “majors”: [“Statistics”, “Data Science”, “Applied Mathematics”, “Computer Science”],
        “hs_prep”: [“AP Statistics”, “AP Calculus”, “AP Computer Science”],
        “alt_paths”: [“Online certificates (Coursera, DataCamp)”],
    },
    “Engineer”: {
        “majors”: [“Mechanical Engineering”, “Civil Engineering”, “Electrical Engineering”, “Chemical Engineering”],
        “hs_prep”: [“AP Physics”, “AP Calculus”, “AP Chemistry”],
        “alt_paths”: [“Engineering Technology (2-year) → B.S.”],
    },
    “Research Scientist”: {
        “majors”: [“Biology”, “Chemistry”, “Physics”, “Neuroscience”, “Biochemistry”],
        “hs_prep”: [“AP Biology”, “AP Chemistry”, “AP Physics”],
        “alt_paths”: [“Research assistant in college → grad school”],
    },
    “Cybersecurity Analyst”: {
        “majors”: [“Cybersecurity”, “Computer Science”, “Information Systems”, “Network Engineering”],
        “hs_prep”: [“AP Computer Science”, “Networking electives”, “AP Statistics”],
        “alt_paths”: [“CompTIA Security+ cert”, “Associate degree + certifications”],
    },
    “Graphic Designer”: {
        “majors”: [“Graphic Design”, “Visual Communication”, “Fine Arts”, “Illustration”],
        “hs_prep”: [“Art”, “Digital Media”, “Photography”],
        “alt_paths”: [“Portfolio school / design bootcamp”],
    },
    “Writer”: {
        “majors”: [“English”, “Creative Writing”, “Journalism”, “Communications”],
        “hs_prep”: [“AP English Language”, “AP English Literature”, “Journalism club”],
        “alt_paths”: [“Self-publish / blog → freelance”],
    },
    “Filmmaker”: {
        “majors”: [“Film Production”, “Cinema Studies”, “Media Arts”, “Communications”],
        “hs_prep”: [“Video Production”, “Photography”, “AP English”],
        “alt_paths”: [“Film festival / YouTube portfolio”, “Community college film program”],
    },
    “UI/UX Designer”: {
        “majors”: [“Human-Computer Interaction”, “Graphic Design”, “Psychology”, “Computer Science”],
        “hs_prep”: [“Art”, “AP Computer Science”, “Psychology”],
        “alt_paths”: [“Google UX Design Certificate (Coursera)”, “Design bootcamp”],
    },
    “Game Designer”: {
        “majors”: [“Game Design”, “Computer Science”, “Digital Media”, “Interactive Media”],
        “hs_prep”: [“AP Computer Science”, “Art”, “Digital Media”],
        “alt_paths”: [“Build indie games → portfolio”, “Modding communities”],
    },
    “Psychologist”: {
        “majors”: [“Psychology”, “Neuroscience”, “Behavioral Science”],
        “hs_prep”: [“AP Psychology”, “AP Biology”, “Statistics”],
        “alt_paths”: [“B.A. Psychology → M.S./Ph.D. required for licensure”],
    },
    “Teacher”: {
        “majors”: [“Education”, “Subject-specific B.A./B.S. + Teaching Credential”],
        “hs_prep”: [“AP courses in your subject area”, “Tutoring / volunteering”],
        “alt_paths”: [“Teach For America (post-grad)”, “Alternative certification programs”],
    },
    “Social Worker”: {
        “majors”: [“Social Work (BSW)”, “Sociology”, “Human Services”, “Psychology”],
        “hs_prep”: [“AP Psychology”, “Sociology”, “Volunteering”],
        “alt_paths”: [“BSW → MSW for clinical licensure”],
    },
    “Counselor”: {
        “majors”: [“Counseling”, “Psychology”, “Social Work”, “Human Development”],
        “hs_prep”: [“AP Psychology”, “Speech / Communication”, “Volunteering”],
        “alt_paths”: [“B.A. Psychology → M.S. Counseling (required for licensure)”],
    },
    “Nurse”: {
        “majors”: [“Nursing (BSN)”, “Biology + Pre-nursing”, “Health Sciences”],
        “hs_prep”: [“AP Biology”, “AP Chemistry”, “Health Science elective”],
        “alt_paths”: [“ADN (2-year) → bridge to BSN”, “CNA while in school”],
    },
    “Mechanical Engineer”: {
        “majors”: [“Mechanical Engineering”, “Industrial Engineering”, “Aerospace Engineering”],
        “hs_prep”: [“AP Physics”, “AP Calculus”, “AP Chemistry”],
        “alt_paths”: [“Engineering Technology A.A.S. → B.S.”],
    },
    “Electrician”: {
        “majors”: [“Electrical Technology (A.A.S.)”, “Electrical Engineering Technology”],
        “hs_prep”: [“Physics”, “Shop/Trade electives”, “Math through Pre-Calc”],
        “alt_paths”: [“Apprenticeship programs (IBEW)”, “Trade/vocational school”],
    },
    “Technician”: {
        “majors”: [“Electronics Technology”, “Computer Technology”, “Industrial Technology”],
        “hs_prep”: [“Physics”, “Shop electives”, “AP Computer Science”],
        “alt_paths”: [“Trade school / associate degree”, “Manufacturer certifications”],
    },
    “Carpenter”: {
        “majors”: [“Construction Management”, “Architecture”, “Building Technology”],
        “hs_prep”: [“Shop / Wood Tech”, “Geometry”, “Technical Drawing”],
        “alt_paths”: [“Apprenticeship (United Brotherhood of Carpenters)”, “Trade school”],
    },
    “Automotive Technician”: {
        “majors”: [“Automotive Technology (A.A.S.)”, “Mechanical Engineering Technology”],
        “hs_prep”: [“Auto shop elective”, “Physics”, “Math”],
        “alt_paths”: [“ASE Certification”, “Manufacturer training programs (Toyota, BMW)”],
    },
    “Entrepreneur”: {
        “majors”: [“Entrepreneurship”, “Business Administration”, “Innovation & Design”],
        “hs_prep”: [“Business electives”, “AP Economics”, “DECA / FBLA clubs”],
        “alt_paths”: [“Start a side project now”, “Incubator programs”, “Self-taught + network”],
    },
    “Business Manager”: {
        “majors”: [“Business Administration (BBA)”, “Management”, “Organizational Leadership”],
        “hs_prep”: [“AP Economics”, “AP Statistics”, “Business electives”],
        “alt_paths”: [“Start in sales/ops → MBA later”],
    },
    “Startup Founder”: {
        “majors”: [“Computer Science”, “Business”, “Engineering”, “Any field with a problem to solve”],
        “hs_prep”: [“AP Computer Science”, “Economics”, “Any technical elective”],
        “alt_paths”: [“Y Combinator / accelerators”, “Build while in school”],
    },
    “Marketing Specialist”: {
        “majors”: [“Marketing”, “Communications”, “Business”, “Psychology”],
        “hs_prep”: [“AP English”, “Economics”, “Art / Digital Media”],
        “alt_paths”: [“Google Digital Marketing Certificate”, “Build social media projects”],
    },
    “Product Manager”: {
        “majors”: [“Business”, “Computer Science”, “Psychology”, “Human-Computer Interaction”],
        “hs_prep”: [“AP Computer Science”, “AP Statistics”, “Business electives”],
        “alt_paths”: [“Start as engineer/designer → move to PM”, “PM bootcamps”],
    },
    “Fitness Instructor”: {
        “majors”: [“Kinesiology”, “Exercise Science”, “Physical Education”],
        “hs_prep”: [“PE”, “Biology”, “Health Science”],
        “alt_paths”: [“NASM / ACE personal trainer cert”, “Associate degree + cert”],
    },
    “Physical Therapist”: {
        “majors”: [“Kinesiology”, “Exercise Science”, “Biology”, “Pre-PT (any science B.S.)”],
        “hs_prep”: [“AP Biology”, “AP Chemistry”, “AP Physics”, “Volunteering at PT clinic”],
        “alt_paths”: [“B.S. → Doctor of Physical Therapy (DPT) required”],
    },
    “Coach”: {
        “majors”: [“Kinesiology”, “Sports Management”, “Physical Education”, “Psychology”],
        “hs_prep”: [“PE”, “Health”, “AP Psychology”],
        “alt_paths”: [“Play at college level”, “Volunteer coaching → paid positions”],
    },
    “Sports Trainer”: {
        “majors”: [“Athletic Training (B.S.)”, “Kinesiology”, “Exercise Science”],
        “hs_prep”: [“AP Biology”, “PE”, “Health Science”],
        “alt_paths”: [“Athletic Training → BOC Exam for certification”],
    },
    “Athletic Director”: {
        “majors”: [“Sports Management”, “Business Administration”, “Physical Education”],
        “hs_prep”: [“Business electives”, “AP Economics”, “Leadership roles”],
        “alt_paths”: [“Coach / administrator experience → AD role”],
    },
}

# Use a 1–5 rating instead of only Yes/No (more accurate + feels more “assessment-like”)
QUESTIONS = [
    {"question": "I enjoy solving puzzles or math problems.", "weights": {"analytical": 2}},
    {"question": "I enjoy sports, physical games, or working out.", "weights": {"athlete": 2}},
    {"question": "I enjoy writing stories, drawing, or designing.", "weights": {"creative": 2}},
    {"question": "I like helping others and talking to people.", "weights": {"social": 2}},
    {"question": "I enjoy working with tools or fixing things.", "weights": {"practical": 2}},
    {"question": "I dream of starting my own business one day.", "weights": {"entrepreneurial": 2}},
    {"question": "I’m curious about science/research and how the world works.", "weights": {"analytical": 1}},
    {"question": "I express myself through music, art, writing, or design.", "weights": {"creative": 1}},
    {"question": "I like teaching, coaching, or mentoring others.", "weights": {"social": 1}},
    {"question": "I enjoy learning about how machines/electronics work.", "weights": {"practical": 1}},
    {"question": "I like taking initiative and making bold decisions.", "weights": {"entrepreneurial": 1}},
    {"question": "I like training and improving my physical performance.", "weights": {"athlete": 1}},
]

RATING_LABELS = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree"
}

# ----------------------------
# Helpers
# ----------------------------
def init_state():
    if "started" not in st.session_state:
        st.session_state.started = False
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "scores" not in st.session_state:
        st.session_state.scores = {c: 0 for c in CATEGORIES}
    if "answers" not in st.session_state:
        st.session_state.answers = []

def reset_quiz():
    st.session_state.started = False
    st.session_state.step = 0
    st.session_state.scores = {c: 0 for c in CATEGORIES}
    st.session_state.answers = []

def apply_answer(q, rating):
    # rating is 1–5, convert into a centered scale so Neutral doesn't inflate scores
    # Map: 1->-2, 2->-1, 3->0, 4->+1, 5->+2
    centered = rating - 3
    for cat, w in q["weights"].items():
        st.session_state.scores[cat] += w * centered

def compute_results():
    items = list(st.session_state.scores.items())
    items_sorted = sorted(items, key=lambda x: x[1], reverse=True)

    top_score = items_sorted[0][1]
    # include ties in top bucket
    top_cats = [cat for cat, score in items_sorted if score == top_score]

    # confidence: bigger gap between #1 and #2 => higher confidence
    if len(items_sorted) > 1:
        gap = items_sorted[0][1] - items_sorted[1][1]
    else:
        gap = top_score

    # Convert gap into 1–6 confidence (simple + readable)
    # (Tweak these thresholds however you want.)
    if gap >= 6:
        conf = 6
    elif gap >= 4:
        conf = 5
    elif gap >= 2:
        conf = 4
    elif gap >= 1:
        conf = 3
    elif gap == 0:
        conf = 2
    else:
        conf = 1

    return items_sorted, top_cats, conf

# ----------------------------
# App
# ----------------------------
init_state()

st.title("🧭 Career Pathfinder")
st.caption("A quick strengths quiz for high school students — discover what you’re naturally good at and careers to explore.")

if not st.session_state.started:
    st.markdown(
        """
        **How it works**
        - You’ll rate a few statements (1–5).
        - We’ll estimate your strongest interest areas.
        - You’ll get career ideas + next steps.
        """
    )
    colA, colB = st.columns(2)
    with colA:
        if st.button("🚀 Start Quiz", use_container_width=True):
            st.session_state.started = True
            st.session_state.step = 0
            st.rerun()
    with colB:
        st.button("ℹ️ About", disabled=True, use_container_width=True)

else:
    total = len(QUESTIONS)
    step = st.session_state.step

    st.progress(min(step / total, 1.0))

    # Question screen
    if step < total:
        q = QUESTIONS[step]

        st.subheader(f"Question {step + 1} of {total}")
        st.write(q["question"])

        rating = st.radio(
            "Choose one:",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{x} — {RATING_LABELS[x]}",
            key=f"rating_{step}",
            horizontal=False
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⬅️ Back", use_container_width=True, disabled=(step == 0)):
                st.session_state.step -= 1
                # remove last answer effects by recalculating from scratch
                # easiest safe method: reset scores and re-apply all answers
                st.session_state.scores = {c: 0 for c in CATEGORIES}
                st.session_state.answers = st.session_state.answers[:-1]
                for idx, saved_rating in enumerate(st.session_state.answers):
                    apply_answer(QUESTIONS[idx], saved_rating)
                st.rerun()

        with col2:
            if st.button("Next ➡️", use_container_width=True):
                # save answer + apply scoring
                st.session_state.answers.append(rating)
                apply_answer(q, rating)
                st.session_state.step += 1
                st.rerun()

        with col3:
            if st.button("🔁 Restart", use_container_width=True):
                reset_quiz()
                st.rerun()

    # Results screen
    else:
        st.success("✅ All questions answered! Here are your results:")

        sorted_scores, top_cats, confidence = compute_results()

        # Show category score chart
        st.subheader("📊 Your Strength Profile")
        chart_data = {CATEGORY_INFO[k]["label"]: v for k, v in sorted_scores}
        st.bar_chart(chart_data)

        st.subheader("🏆 Your Top Strength Areas")
        for cat, score in sorted_scores[:3]:
            info = CATEGORY_INFO[cat]
            st.markdown(f"**{info['label']}** — {score} points")
            st.caption(info["desc"])

        st.markdown("---")

        st.subheader("💼 Career Ideas to Explore")
        for cat, score in sorted_scores[:3]:
            st.markdown(f"**{CATEGORY_INFO[cat]['label']}**")
            for career in CAREER_OPTIONS[cat]:
                st.markdown(f"- {career}")

        st.markdown("---")

        # College Roadmap section
        st.subheader("🎓 College Roadmap")
        st.caption("For each top career, here are the college majors and high school courses that build toward it.")

        for cat, score in sorted_scores[:2]:  # top 2 categories to keep it focused
            label = CATEGORY_INFO[cat]["label"]
            st.markdown(f"### {label} Careers")
            for career in CAREER_OPTIONS[cat][:3]:  # top 3 careers per category
                roadmap = CAREER_ROADMAP.get(career)
                if not roadmap:
                    continue
                with st.expander(f"📌 {career}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**College Majors to Consider**")
                        for major in roadmap["majors"]:
                            st.markdown(f"- {major}")
                        st.markdown("**High School Prep Courses**")
                        for course in roadmap["hs_prep"]:
                            st.markdown(f"- {course}")
                    with col_b:
                        st.markdown("**Alternative Paths**")
                        for path in roadmap["alt_paths"]:
                            st.markdown(f"- {path}")

        st.markdown("---")

        # Confidence with tie explanation
        st.subheader("🎯 Confidence Level")
        if len(top_cats) > 1:
            st.info(f"Confidence: {confidence}/6 — You had a tie for your top strength area, so results are more blended.")
        else:
            st.info(f"Confidence: {confidence}/6 — This reflects how separated your top score is from the next score.")

        st.subheader("✅ Next Steps (so it’s a real “career map”)")
        st.markdown(
            """
            Pick **one** career from your top area and do:
            - Watch a day-in-the-life video (YouTube)
            - Find 2 high school clubs or projects that match it
            - Look up 1 certification or beginner course
            - Talk to 1 adult who works near that field (teacher, family friend, counselor)
            """
        )

        colX, colY = st.columns(2)
        with colX:
            if st.button("🔁 Retake Quiz", use_container_width=True):
                reset_quiz()
                st.rerun()
        with colY:
            if st.button("🏁 Finish", use_container_width=True):
                st.balloons()