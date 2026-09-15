"""
Generate a clean, professional, non-bloated 14-slide presentation
for demoing the AI Meeting Intelligence Companion.
Strictly under 15 slides, concise, visually clear, and focused on:
- Features
- Architecture
- Technologies used
- Demo flow
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_demo_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Clean Dark Modern Theme (Obsidian & Indigo)
    COLOR_BG = RGBColor(15, 23, 42)          # Slate 900 (#0F172A)
    COLOR_CARD = RGBColor(30, 41, 59)        # Slate 800 (#1E293B)
    COLOR_CARD_BORDER = RGBColor(51, 65, 85) # Slate 700 (#334155)
    COLOR_PRIMARY = RGBColor(99, 102, 241)   # Indigo 500 (#6366F1)
    COLOR_ACCENT = RGBColor(45, 212, 191)    # Teal 400 (#2DD4BF)
    COLOR_SUCCESS = RGBColor(52, 211, 153)   # Emerald 400 (#34D399)
    COLOR_AMBER = RGBColor(251, 191, 36)     # Amber 400 (#FBBF24)
    COLOR_WHITE = RGBColor(248, 250, 252)    # Slate 50 (#F8FAFC)
    COLOR_MUTED = RGBColor(148, 163, 184)    # Slate 400 (#94A3B8)

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_slide_header(slide, badge_text, title, subtitle=None):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.3))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Badge / Section
        p_badge = tf.paragraphs[0]
        p_badge.text = badge_text.upper()
        p_badge.font.size = Pt(10)
        p_badge.font.bold = True
        p_badge.font.color.rgb = COLOR_PRIMARY
        p_badge.space_after = Pt(4)

        # Title
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

        # Subtitle
        if subtitle:
            p_title.space_after = Pt(4)
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = COLOR_MUTED

    def add_card(slide, left, top, width, height, title, points, badge=None, border_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_CARD
        shape.line.color.rgb = border_color if border_color else COLOR_CARD_BORDER
        shape.line.width = Pt(1)

        tb = slide.shapes.add_textbox(left + Inches(0.28), top + Inches(0.22), width - Inches(0.56), height - Inches(0.44))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p0 = tf.paragraphs[0]
        if badge:
            r_badge = p0.add_run()
            r_badge.text = f"[{badge}] "
            r_badge.font.size = Pt(10)
            r_badge.font.bold = True
            r_badge.font.color.rgb = COLOR_ACCENT

        r_title = p0.add_run()
        r_title.text = title
        r_title.font.size = Pt(15)
        r_title.font.bold = True
        r_title.font.color.rgb = COLOR_WHITE
        p0.space_after = Pt(10)

        for pt in points:
            p = tf.add_paragraph()
            if isinstance(pt, tuple):
                bold_part, regular_part = pt
                r_b = p.add_run()
                r_b.text = f"• {bold_part}: "
                r_b.font.bold = True
                r_b.font.size = Pt(12)
                r_b.font.color.rgb = COLOR_WHITE

                r_r = p.add_run()
                r_r.text = regular_part
                r_r.font.size = Pt(12)
                r_r.font.color.rgb = COLOR_MUTED
            else:
                p.text = f"• {pt}"
                p.font.size = Pt(12)
                p.font.color.rgb = COLOR_MUTED
            p.space_after = Pt(6)

    def add_speaker_notes(slide, notes):
        ns = slide.notes_slide
        ns.notes_text_frame.text = notes.strip()

    # =========================================================================
    # SLIDE 1: Title
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(3.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "AI MEETING INTELLIGENCE COMPANION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(8)

    p = tf1.add_paragraph()
    p.text = "Turning Meeting Conversations\nInto Actionable Intelligence"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(16)

    p = tf1.add_paragraph()
    p.text = "Automated speech transcription, structured intelligence extraction, human-governed tasks, and semantic meeting memory."
    p.font.size = Pt(15)
    p.font.color.rgb = COLOR_MUTED

    # Bottom pill badges
    pill_box = s1.shapes.add_textbox(Inches(1.0), Inches(5.8), Inches(11.3), Inches(0.8))
    tf_pill = pill_box.text_frame
    p = tf_pill.paragraphs[0]
    p.text = "Tech: FastAPI  |  React + Vite  |  faster-whisper  |  Groq LLM  |  FAISS Vector Search  |  SQLite"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_ACCENT

    add_speaker_notes(s1, "Welcome everyone. Today I'm demoing the AI Meeting Intelligence Companion. It's built to capture meeting recordings, extract structured intelligence, and help teams follow through on verbal commitments.")

    # =========================================================================
    # SLIDE 2: The Problem
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_slide_header(s2, "The Challenge", "The Reality of Modern Meetings", "Valuable decisions and commitments get lost the moment a meeting ends.")

    add_card(s2, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "Lost Commitments", [
        ("Verbal promises", "Action items are spoken during meetings but never written down."),
        ("No owner or date", "Tasks lack clear ownership, deadlines, and tracking."),
        ("Dropped balls", "Projects stall because nobody remembers who committed to what.")
    ], border_color=COLOR_AMBER)

    add_card(s2, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "Note-Taking Friction", [
        ("Distracted attendees", "Taking manual notes prevents active participation in discussions."),
        ("Incomplete records", "Minutes are often subjective, rushed, and miss key nuances."),
        ("Wasted effort", "Hours spent writing summaries that nobody reads later.")
    ], border_color=COLOR_AMBER)

    add_card(s2, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "Unsearchable Knowledge", [
        ("Dead recordings", "Audio/video recordings sit in cloud folders completely unindexed."),
        ("No recall", "Finding a past agreement requires scrubbing through 1-hour audio files."),
        ("Organizational amnesia", "Teams re-discuss the same topics across multiple weeks.")
    ], border_color=COLOR_AMBER)

    add_speaker_notes(s2, "The core problem: teams spend hours in meetings, but the knowledge evaporates immediately. Notes are incomplete, audio files are unsearchable, and action items get dropped.")

    # =========================================================================
    # SLIDE 3: The Solution (Product Definition)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_slide_header(s3, "Product Overview", "What is the AI Meeting Intelligence Companion?", "A dedicated intelligence layer that operates after the meeting ends.")

    add_card(s3, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "What This Application IS", [
        ("Post-Meeting Intelligence Engine", "Ingests recorded audio files or in-browser live recordings."),
        ("Verifiable Speech-to-Text", "Transcribes audio locally with millisecond-exact segment timestamps."),
        ("Structured AI Extraction", "Extracts summaries, action items, consensus decisions, and delivery risks."),
        ("Human-Governed Workflow", "Allows team leads to review, edit, assign, and confirm items before dispatch."),
        ("Semantic Cross-Meeting Search", "Instant vector search & Q&A across your entire historical meeting archive.")
    ], border_color=COLOR_SUCCESS)

    add_card(s3, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.7), "What This Application IS NOT", [
        ("NOT a Conferencing App", "Does not host video calls, manage cameras, or replace Zoom/Google Meet."),
        ("NOT an Autonomous Agent", "Does not make decisions or send emails without human review and approval."),
        ("NOT a Heavy Third-Party Tool", "No mandatory Jira, Trello, or n8n dependencies—everything works standalone."),
        ("NOT Cloud-Dependent for Audio", "Speech transcription and vector retrieval run on your own infrastructure.")
    ], border_color=COLOR_PRIMARY)

    add_speaker_notes(s3, "Important framing: this is NOT another conferencing tool. The meeting happens wherever you want. Our companion is the intelligent post-meeting hub that processes the recording, extracts structured data, and enforces human-in-the-loop review.")

    # =========================================================================
    # SLIDE 4: Architecture
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_slide_header(s4, "System Architecture", "How the System Works End-to-End", "A clean, modular 3-tier architecture with clear separation of responsibilities.")

    add_card(s4, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "1. Frontend (React 18)", [
        ("Vite + Tailwind CSS", "Fast, responsive single-page app with clean dark enterprise theme."),
        ("Audio Ingestion Hub", "Drag-and-drop file upload & live mic recording."),
        ("Granular Inline UI", "Per-card edit controls for tasks, owners, emails, and calendar events."),
        ("Unified Workspaces", "Dashboard, Meetings, Tasks, Calendar, Review, Decisions, Search.")
    ], border_color=COLOR_PRIMARY)

    add_card(s4, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "2. Backend (FastAPI)", [
        ("High-Performance API", "FastAPI on Python 3.11 with asynchronous endpoints."),
        ("Acoustic Ingestion", "Local speech transcription via faster-whisper (CTranslate2)."),
        ("Structured Extraction", "Groq Cloud LLM API with strict JSON schema enforcement."),
        ("Event Notification", "Built-in SMTP transactional email service.")
    ], border_color=COLOR_ACCENT)

    add_card(s4, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "3. Persistence & Search", [
        ("SQLite System of Record", "9 normalized relational tables; tracks mutable state & full audit history."),
        ("Safe PRAGMA Migrations", "Schema upgrades run without dropping tables or losing existing records."),
        ("Local FAISS Vector Index", "Indexes unedited transcript chunks for instant semantic search."),
        ("RAG Engine", "Combines FAISS chunks with Groq for grounded question answering.")
    ], border_color=COLOR_SUCCESS)

    add_speaker_notes(s4, "Here is our 3-tier architecture: React frontend for intuitive human governance, FastAPI backend orchestrating transcription and extraction, and a dual persistence model: SQLite for business state and FAISS for semantic search.")

    # =========================================================================
    # SLIDE 5: Tech Stack
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_slide_header(s5, "Technology Stack", "Core Technologies & Libraries", "Carefully selected tools prioritizing performance, simplicity, and low operational overhead.")

    add_card(s5, Inches(0.8), Inches(2.0), Inches(5.6), Inches(2.25), "Frontend Stack", [
        ("React 18 & Vite", "Ultra-fast HMR and modular component rendering."),
        ("Tailwind CSS", "Utility-first modern dark enterprise UI styling."),
        ("React Router DOM", "Seamless client-side navigation across 8 workspaces.")
    ], badge="Client")

    add_card(s5, Inches(6.8), Inches(2.0), Inches(5.7), Inches(2.25), "Backend & Ingestion", [
        ("FastAPI & Uvicorn", "High-throughput asynchronous Python web framework."),
        ("faster-whisper", "CTranslate2 implementation; 4x faster local speech-to-text."),
        ("Pydantic v2", "Strict schema validation and structured JSON serialization.")
    ], badge="Backend")

    add_card(s5, Inches(0.8), Inches(4.45), Inches(5.6), Inches(2.25), "AI & Vector Search", [
        ("Groq Cloud API", "Ultra-low-latency LPU inference for structured extraction & RAG."),
        ("sentence-transformers", "all-MiniLM-L6-v2 local 384-dimensional dense embeddings."),
        ("FAISS (CPU)", "Facebook AI Similarity Search; in-memory vector index (<2ms).")
    ], badge="AI / ML")

    add_card(s5, Inches(6.8), Inches(4.45), Inches(5.7), Inches(2.25), "Database & Dispatch", [
        ("SQLite 3", "Embedded zero-config database with safe ALTER TABLE migrations."),
        ("Python smtplib", "Standard-library transactional email notifications (zero deps)."),
        ("python-dotenv", "Secure environment configuration for credentials and keys.")
    ], badge="Storage")

    add_speaker_notes(s5, "Notice the technology choices: no heavy message brokers, no cloud database fees, no bloated libraries. Everything runs locally or via high-speed API calls.")

    # =========================================================================
    # SLIDE 6: Feature 1 - Transcription & Executive Summaries
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_slide_header(s6, "Core Feature", "Audio Ingestion & Executive Summaries", "Turn raw meeting audio into time-synchronized transcripts and executive digests.")

    add_card(s6, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "Acoustic Transcription", [
        ("Format Support", "Accepts MP3, WAV, M4A, and MP4 audio recordings."),
        ("Live Web Recording", "Record directly in-browser using your microphone with live elapsed timer."),
        ("Segmented Timestamps", "Every speech segment is indexed with exact start and end timestamps (e.g. 02:45 - 03:10)."),
        ("Local Privacy", "Audio files are processed locally via faster-whisper without cloud transmission fees.")
    ], border_color=COLOR_PRIMARY)

    add_card(s6, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.7), "Executive Summaries", [
        ("Key Discussion Points", "Concise bullet-point digest capturing core themes of the conversation."),
        ("Global Edit Support", "Meeting titles and summary points can be edited and refined by admins."),
        ("Meeting Library", "All processed meetings are cataloged with timestamps, summary previews, and navigation links."),
        ("Zero Scrubbing", "Read what happened in 30 seconds instead of listening to a 45-minute recording.")
    ], border_color=COLOR_ACCENT)

    add_speaker_notes(s6, "Feature 1 is ingestion and summaries. Users can drag-and-drop an audio file or record directly with the microphone. The system transcribes every sentence with exact timestamps and generates an executive summary.")

    # =========================================================================
    # SLIDE 7: Feature 2 - Action Items & Human Governance
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_slide_header(s7, "Core Feature", "Smart Action Items & Human Governance", "AI detects proposed commitments; humans review, refine, and authorize execution.")

    add_card(s7, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "1. AI Extraction", [
        ("Automated Detection", "Extracts task description, suggested owner, and due date."),
        ("Confidence Scoring", "Rates confidence (0-100%) so users know reliability."),
        ("Safe Initial State", "Always initialized as 'Pending Review'—never auto-executes.")
    ], border_color=COLOR_AMBER)

    add_card(s7, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "2. Inline Editing", [
        ("Per-Item Edit Form", "Edit task, owner, owner email, and due date on each card."),
        ("Stay in Pending", "Saving edits persists to SQLite but keeps the item Pending Review."),
        ("Audit History Trail", "Every change is logged in action_item_history (old value -> new value)."),
        ("Human Modified Tag", "Clearly displays 'Edited by human' on modified records.")
    ], border_color=COLOR_PRIMARY)

    add_card(s7, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "3. Explicit Confirm", [
        ("Human Authorization", "Admin clicks 'Confirm' only when the task and assignee are ready."),
        ("Execution Trigger", "Moves item to confirmed tasks board and triggers email notification."),
        ("Dismiss & Reopen", "Dismiss false positives or reopen closed items at any time."),
        ("Full Control", "The LLM never modifies external systems directly.")
    ], border_color=COLOR_SUCCESS)

    add_speaker_notes(s7, "Feature 2 is our governance model. AI extracts tasks with confidence scores, but they enter 'Pending Review'. Admins can edit the task, assign the owner's email, and save changes. Every edit is audit-logged. Only explicit human confirmation activates the task.")

    # =========================================================================
    # SLIDE 8: Feature 3 - Tasks Board & Email Notifications
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_slide_header(s8, "Core Feature", "Centralized Tasks & Email Notifications", "Confirmed action items become actionable tasks with automatic notification.")

    add_card(s8, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "Centralized Tasks Page (/tasks)", [
        ("Actionable Task Board", "Consolidates confirmed commitments across all analyzed meetings."),
        ("Status Filtering", "Filter by All, Confirmed, or Dismissed tasks with real-time counts."),
        ("Meeting Lineage", "Every task links directly back to its originating meeting transcript."),
        ("Clear Metadata", "Displays task title, assigned owner, email, due date, and timestamp badge."),
        ("Executive Visibility", "Total confirmed task count displayed directly on the main Dashboard.")
    ], border_color=COLOR_SUCCESS)

    add_card(s8, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.7), "Transactional Email Dispatch", [
        ("Post-Commit Safety", "Email dispatches ONLY after SQLite confirmation has successfully committed."),
        ("Direct UI Recipient", "Uses the owner_email specified in the task card."),
        ("Clean Plain-Text Body", "Emails the owner with Task title, Due date, and Meeting name."),
        ("Duplicate Prevention", "email_sent flag guarantees assignees are never spammed if an item is reopened and reconfirmed."),
        ("Fault Tolerant", "If SMTP is unconfigured, task confirmation still succeeds without errors.")
    ], border_color=COLOR_PRIMARY)

    add_speaker_notes(s8, "Feature 3: The Tasks workspace and email delivery. Confirmed tasks appear on a clean board with source meeting links. When confirmed, an email is automatically sent to the owner's email via SMTP, with built-in duplicate protection.")

    # =========================================================================
    # SLIDE 9: Feature 4 - Decisions, Risks & Meeting Requests
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_slide_header(s9, "Core Feature", "Decisions, Risks & Follow-Up Requests", "Capturing organizational consensus, delivery blockers, and scheduling intent.")

    add_card(s9, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "Decisions Captured", [
        ("Consensus Extraction", "Identifies explicit agreements made during discussions."),
        ("Decisions Catalog", "Dedicated /decisions page aggregating business choices across all meetings."),
        ("Audit Verification", "Includes source timestamps linking back to exact spoken moments."),
        ("Editable", "Admins can refine decision wording directly in the interface.")
    ], border_color=COLOR_SUCCESS)

    add_card(s9, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "Risks & Blockers", [
        ("Early Threat Detection", "Flags technical bottlenecks, dependency risks, and timeline threats."),
        ("Confidence Ratings", "Provides confidence percentages for each detected risk."),
        ("Timestamped Evidence", "Pinpoints where in the meeting the risk was voiced."),
        ("Proactive Governance", "Prevents surprises before work begins.")
    ], border_color=COLOR_AMBER)

    add_card(s9, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "Meeting Requests", [
        ("Follow-up Intent", "Detects spoken requests for future syncs or reviews."),
        ("Verbatim Scheduling", "Preserves exact phrases like 'next Friday' or 'Sept 20th at 3 PM'."),
        ("Pending Review", "Feeds into the internal Calendar page for approval or dismissal."),
        ("Traceable", "Linked to the originating meeting context.")
    ], border_color=COLOR_PRIMARY)

    add_speaker_notes(s9, "Feature 4: Beyond tasks, our AI captures Decisions, Risks, and Meeting Requests. Decisions build a company-wide consensus catalog; Risks flag blockers early; Meeting Requests feed into our internal calendar.")

    # =========================================================================
    # SLIDE 10: Feature 5 - Calendar & Internal Scheduling
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_slide_header(s10, "Core Feature", "Internal Calendar & Scheduling", "Dual-source event tracking separating AI suggestions from manual events.")

    add_card(s10, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "AI-Suggested Requests (Pending)", [
        ("Extracted from Audio", "Follow-ups mentioned by participants during meetings."),
        ("Pending Triage", "Listed under 'Pending Review' until confirmed or dismissed."),
        ("Inline Date Refinement", "Admins can edit topic, proposed date, and proposed time."),
        ("One-Click Confirmation", "Clicking 'Confirm Event' converts it into a confirmed calendar commitment.")
    ], border_color=COLOR_AMBER)

    add_card(s10, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.7), "Manual Event Creation (+ Add Event)", [
        ("Direct Human Scheduling", "Click '+ Add Event' to create custom events anytime."),
        ("Simple Modal Form", "Captures Title (required), Date (required), Time, and Notes."),
        ("Immediate Confirmation", "Automatically marked confirmed upon creation (source = 'manual')."),
        ("Full CRUD Lifecycle", "Edit or delete manual events directly from the calendar list."),
        ("Visual Differentiation", "Clearly labeled 'AI Suggested' vs. 'Manually Created'.")
    ], border_color=COLOR_SUCCESS)

    add_speaker_notes(s10, "Feature 5 is our internal Calendar. It has two distinct sources: AI-detected requests that need review, and a '+ Add Event' modal for manual human scheduling. Both live cleanly in one place with distinct badges.")

    # =========================================================================
    # SLIDE 11: Feature 6 - Semantic Search & "Ask AI" (RAG)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s11)
    add_slide_header(s11, "Core Feature", "Semantic Search & 'Ask AI' Assistant", "Search by concept and ask conversational questions grounded in transcript facts.")

    add_card(s11, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "Semantic Vector Search (/search)", [
        ("Conceptual Matching", "Finds relevant discussions even when query words don't match exact spoken text."),
        ("Dense Embeddings", "Uses local 384-dimensional sentence-transformer embeddings."),
        ("Sub-Millisecond Search", "In-memory FAISS flat inner-product vector store (<2ms response)."),
        ("Instant Previews", "Returns ranked results with meeting names, timestamps, and confidence scores.")
    ], border_color=COLOR_PRIMARY)

    add_card(s11, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.7), "Grounded 'Ask AI' Assistant (RAG)", [
        ("Conversational Q&A", "Ask questions like 'What did the team agree on regarding database backup?'"),
        ("Strict Grounding Context", "Retrieves top-5 transcript chunks and injects them into the prompt."),
        ("Zero Hallucination", "Temperature = 0.0; model is instructed to answer ONLY from evidence."),
        ("Clickable Citations", "Displays direct answers alongside exact transcript segment quotes and timestamps.")
    ], border_color=COLOR_ACCENT)

    add_speaker_notes(s11, "Feature 6 is our neural memory. Semantic Search allows users to find concepts across past meetings, and the 'Ask AI' drawer uses RAG with temperature zero to provide factual answers backed by clickable citations.")

    # =========================================================================
    # SLIDE 12: Technical Highlights & Privacy
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s12)
    add_slide_header(s12, "Engineering Highlights", "Privacy, Data Integrity & Performance", "Key architectural choices ensuring enterprise-grade reliability.")

    add_card(s12, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "Privacy-First Architecture", [
        ("Local Speech-to-Text", "Audio files are transcribed locally via faster-whisper on CPU/GPU."),
        ("Local Vector Storage", "FAISS vectors and embeddings stay entirely on your server."),
        ("Minimal Data Exposure", "Only sanitized transcript text is sent to Groq for extraction."),
        ("Zero Audio Uploads", "Raw recordings never leave your infrastructure.")
    ], border_color=COLOR_SUCCESS)

    add_card(s12, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "Safe Data Migrations", [
        ("Dynamic PRAGMA Checks", "Migrations inspect columns before executing ALTER TABLE."),
        ("No Table Drops", "Tables are never deleted or recreated; existing data is preserved."),
        ("Nullable Fields", "New columns like owner_email are nullable for backward compatibility."),
        ("Audit Trail", "Field-level change history tracked in action_item_history.")
    ], border_color=COLOR_PRIMARY)

    add_card(s12, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "Blazing Performance", [
        ("Fast Inference", "Groq LPU processes full meeting transcripts in 1-3 seconds."),
        ("Fast Transcription", "faster-whisper provides up to 4x speedup via CTranslate2."),
        ("In-Memory Search", "FAISS vector lookups execute in under 2 milliseconds."),
        ("Lightweight Bundle", "Vite production frontend builds in ~500ms.")
    ], border_color=COLOR_ACCENT)

    add_speaker_notes(s12, "Engineering highlights: Privacy is preserved because audio stays local. Data migrations are non-destructive using PRAGMA inspection. And performance is blazing fast across transcription, Groq inference, and FAISS.")

    # =========================================================================
    # SLIDE 13: Live Demo Flow
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s13)
    add_slide_header(s13, "Live Demonstration", "What We Will See in Today's Demo", "A step-by-step walkthrough of the live application.")

    add_card(s13, Inches(0.8), Inches(2.0), Inches(2.7), Inches(4.7), "Step 1: Ingest", [
        ("Go to /assistant", "Open audio hub."),
        ("Upload or Record", "Drop a meeting file or record live audio."),
        ("Pipeline Status", "Watch real-time transcription and intelligence extraction.")
    ], badge="1. Ingest", border_color=COLOR_PRIMARY)

    add_card(s13, Inches(3.8), Inches(2.0), Inches(2.7), Inches(4.7), "Step 2: Inspect", [
        ("Overview & Summary", "Review executive bullet points."),
        ("Decisions & Risks", "Inspect captured consensus and delivery blockers."),
        ("Transcript", "See millisecond timestamps synced to audio.")
    ], badge="2. Inspect", border_color=COLOR_ACCENT)

    add_card(s13, Inches(6.8), Inches(2.0), Inches(2.7), Inches(4.7), "Step 3: Govern", [
        ("Inline Action Edit", "Edit task, owner, and owner email."),
        ("Verify Pending", "Save change; confirm item remains pending."),
        ("Confirm Task", "Confirm task; triggers email notification.")
    ], badge="3. Govern", border_color=COLOR_AMBER)

    add_card(s13, Inches(9.8), Inches(2.0), Inches(2.7), Inches(4.7), "Step 4: Execute", [
        ("Tasks Page", "See confirmed task on /tasks board."),
        ("Calendar Page", "Confirm AI request & add manual event."),
        ("Ask AI", "Ask a conversational question with citations.")
    ], badge="4. Execute", border_color=COLOR_SUCCESS)

    add_speaker_notes(s13, "This is our live demo flow today: 1) Upload or record audio, 2) Inspect the extracted intelligence and transcript, 3) Edit and confirm an action item, and 4) View tasks, calendar scheduling, and test Ask AI.")

    # =========================================================================
    # SLIDE 14: Summary & Q&A
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s14)

    tb14 = s14.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(4.0))
    tf14 = tb14.text_frame
    tf14.word_wrap = True

    p = tf14.paragraphs[0]
    p.text = "AI MEETING INTELLIGENCE COMPANION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_PRIMARY
    p.space_after = Pt(8)

    p = tf14.add_paragraph()
    p.text = "Summary & Key Takeaways"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_after = Pt(16)

    takeaways = [
        "Eliminates the 'Post-Meeting Memory Hole' with automated transcription & structured intelligence.",
        "Human-in-the-loop governance: AI detects and proposes, but humans review, edit, and authorize.",
        "Dual-store persistence: SQLite for business state; FAISS for immutable evidence & semantic search.",
        "Production-ready & lightweight: Runs standalone with local speech decoding, Groq LPU, and zero bloat."
    ]

    for t in takeaways:
        p = tf14.add_paragraph()
        p.text = f"✔  {t}"
        p.font.size = Pt(15)
        p.font.color.rgb = COLOR_SUCCESS
        p.space_after = Pt(8)

    p_qa = tf14.add_paragraph()
    p_qa.space_before = Pt(20)
    p_qa.text = "Thank you! Open for Questions & Live Demo."
    p_qa.font.size = Pt(20)
    p_qa.font.bold = True
    p_qa.font.color.rgb = COLOR_ACCENT

    add_speaker_notes(s14, "To conclude: The AI Meeting Intelligence Companion bridges conversational meetings with structured execution. Thank you, and I am now ready to begin the live demo and take your questions.")

    output_path = os.path.abspath(r"c:\Users\Aditya N\Downloads\projects\businessbuddy\AI_Meeting_Intelligence_Companion_Demo.pptx")
    prs.save(output_path)
    print(f"Clean demo presentation created successfully at: {output_path}")

if __name__ == "__main__":
    build_demo_deck()
