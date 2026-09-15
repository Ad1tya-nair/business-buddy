"""
Generate a professional, 16-slide widescreen (16:9) presentation for the
AI Meeting Intelligence Companion project.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6]  # Blank layout

    # Color Palette - Professional Modern Tech Dark Enterprise
    BG_DARK = RGBColor(11, 15, 25)          # #0B0F19 Deep obsidian slate
    SURFACE_CARD = RGBColor(23, 32, 51)     # #172033 Elevated card slate
    SURFACE_BORDER = RGBColor(45, 59, 85)   # #2D3B55 Subtle border
    ACCENT_INDIGO = RGBColor(99, 102, 241)  # #6366F1 Brand Indigo
    ACCENT_EMERALD = RGBColor(16, 185, 129) # #10B981 Success / Confirmed
    ACCENT_AMBER = RGBColor(245, 158, 11)   # #F59E0B Warning / Pending
    ACCENT_CYAN = RGBColor(6, 182, 212)     # #06B6D4 Tech highlight
    TEXT_WHITE = RGBColor(248, 250, 252)    # #F8FAFC Primary text
    TEXT_MUTED = RGBColor(148, 163, 184)    # #94A3B8 Secondary text
    TEXT_DIM = RGBColor(100, 116, 139)      # #64748B Tertiary text

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, category, title, subtitle=None):
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.3))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Category / Kicker
        p_cat = tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_INDIGO
        p_cat.space_after = Pt(4)

        # Title
        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

        # Subtitle
        if subtitle:
            p_title.space_after = Pt(4)
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title, items, border_accent=None, title_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = SURFACE_CARD
        if border_accent:
            card.line.color.rgb = border_accent
            card.line.width = Pt(1.5)
        else:
            card.line.color.rgb = SURFACE_BORDER
            card.line.width = Pt(1)

        tx_box = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        if title:
            p_head = tf.paragraphs[0]
            p_head.text = title
            p_head.font.size = Pt(15)
            p_head.font.bold = True
            p_head.font.color.rgb = title_color if title_color else TEXT_WHITE
            p_head.space_after = Pt(10)

        for i, item in enumerate(items):
            p = tf.add_paragraph() if (title or i > 0) else tf.paragraphs[0]
            if isinstance(item, tuple):
                header, desc = item
                r_head = p.add_run()
                r_head.text = f"• {header}: "
                r_head.font.bold = True
                r_head.font.color.rgb = ACCENT_INDIGO
                r_head.font.size = Pt(12)
                
                r_desc = p.add_run()
                r_desc.text = desc
                r_desc.font.color.rgb = TEXT_MUTED
                r_desc.font.size = Pt(12)
            else:
                p.text = f"• {item}"
                p.font.size = Pt(12)
                p.font.color.rgb = TEXT_MUTED
            p.space_after = Pt(6)

    def set_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text.strip()

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s1)

    # Decorative accent bar
    accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.2), Inches(0.6), Inches(0.08))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = ACCENT_INDIGO
    accent_bar.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(2.5), Inches(10.8), Inches(3.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p1 = tf1.paragraphs[0]
    p1.text = "AI Meeting Intelligence Companion"
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_after = Pt(10)

    p2 = tf1.add_paragraph()
    p2.text = "From Passive Audio Recordings to Actionable Structured Intelligence"
    p2.font.size = Pt(20)
    p2.font.color.rgb = ACCENT_CYAN
    p2.space_after = Pt(24)

    p3 = tf1.add_paragraph()
    p3.text = "A Complete Technical Architecture, Data Lifecycle, & Live Product Demo Overview"
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_MUTED

    # Meta box bottom
    meta_box = s1.shapes.add_textbox(Inches(1.2), Inches(5.8), Inches(10.8), Inches(0.8))
    tf_meta = meta_box.text_frame
    p_meta = tf_meta.paragraphs[0]
    p_meta.text = "Stack: FastAPI (Python 3.11) | faster-whisper | Groq (Llama-3/Qwen) | FAISS Vector Store | React 18 & Vite"
    p_meta.font.size = Pt(12)
    p_meta.font.color.rgb = ACCENT_INDIGO

    set_notes(s1, """
WELCOME & INTRO:
"Welcome everyone. Today I'm presenting the AI Meeting Intelligence Companion.
First, a critical clarification: This is NOT another Zoom, Teams, or conferencing tool. The actual meeting happens wherever people collaborate.
Our product is the post-meeting intelligence brain: it ingests conversational audio recordings, extracts audit-grade structured intelligence, enforces human-in-the-loop governance, and provides semantic search and RAG retrieval over past decisions. Let's walk through how it works."
""")

    # =========================================================================
    # SLIDE 2: Executive Summary & Problem Space
    # =========================================================================
    s2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Context", "The 'Post-Meeting Memory Hole' in Modern Business",
               "Why traditional video meetings fail at accountability and knowledge retention")

    add_card(s2, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "The Critical Friction", [
        ("Information Dissipation", "Conversations generate crucial commitments, dates, and risks that evaporate within 48 hours without rigorous notes."),
        ("Manual Note-Taking Cost", "Engineers and managers waste 15-20% of meeting time scribbling incomplete, biased, and unsearchable minutes."),
        ("No Execution Bridge", "Verbal agreements fail to convert into assignable tasks, resulting in dropped action items and unaligned teams."),
        ("Zero Searchability", "Hours of recorded audio sit inert in storage buckets—unindexed and impossible to query semantically.")
    ], border_accent=ACCENT_AMBER)

    add_card(s2, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "The Companion Solution", [
        ("Zero-Overhead Ingestion", "Upload any meeting recording or record live via browser; automated background processing takes over."),
        ("Deep Semantic Extraction", "Extracts tasks, assignees, dates, confidence scores, risks, and consensus decisions using high-speed LLMs."),
        ("Human-in-the-Loop Governance", "AI extracts suggestions; humans review, refine, and explicitly authorize execution before any external trigger."),
        ("Interactive Neural Recall", "Sub-second vector retrieval and grounded RAG answer natural-language queries with verbatim transcript citations.")
    ], border_accent=ACCENT_EMERALD)

    add_card(s2, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "Core Design Principles", [
        ("Simplicity & Reliability", "No microservice sprawl. Clean monolithic architecture using FastAPI and embedded SQLite."),
        ("Local-First Privacy", "Transcripts and vector index remain local; only sanitized intelligence prompts touch high-speed Groq inference."),
        ("Auditable System of Record", "Every human modification is versioned with field-level delta history in SQLite."),
        ("Immediate Production ROI", "No complex enterprise onboarding, OAuth setups, or Jira/Trello dependencies required.")
    ], border_accent=ACCENT_INDIGO)

    set_notes(s2, """
TALKING POINTS:
"We identified the single biggest drain on enterprise productivity: the post-meeting memory hole. 
Decisions are made verbally, but they never reach the project board. Or worse, two people leave with conflicting memories of who owns what.
Our companion bridges this gap without forcing teams to adopt another complicated SaaS ecosystem. It listens, extracts, governs, and remembers."
""")

    # =========================================================================
    # SLIDE 3: High-Level Architecture Topology
    # =========================================================================
    s3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s3)
    add_header(s3, "Architecture Overview", "End-to-End System Topology & Data Flow",
               "Clean separation between presentation, ingestion, persistence, and neural search")

    add_card(s3, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Client Tier (React + Vite)", [
        ("Dark Enterprise SaaS UI", "Tailwind CSS dark aesthetic with responsive tables, cards, and modal drawers."),
        ("Media Recording Engine", "Web Audio API / MediaRecorder for live in-browser audio capture with elapsed timer."),
        ("Fine-Grained Inline State", "Per-item edit states for action items and calendar events without page reloads."),
        ("REST API Abstraction", "Centralized api.js service wrapping all async HTTP fetch calls with graceful error recovery.")
    ])

    add_card(s3, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "Core Application Tier (FastAPI)", [
        ("Asynchronous Orchestration", "Single unified FastAPI server with multi-part audio streaming & JSON endpoints."),
        ("Speech-to-Text Pipeline", "faster-whisper local engine performing multi-speaker timestamped transcription."),
        ("LLM Intelligence Engine", "Groq cloud integration executing structured JSON mode prompts with strict Pydantic models."),
        ("Transactional Dispatcher", "SMTP transactional email handler triggered only upon database commit.")
    ], border_accent=ACCENT_INDIGO)

    add_card(s3, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "Persistence & Retrieval Tier", [
        ("Relational Source of Record", "SQLite (meeting_intelligence.db) tracking 9 normalized tables and migration versioning."),
        ("Audit Delta Tracking", "action_item_history table storing field-level diffs (old_value, new_value, timestamp)."),
        ("Dense Embedding Store", "sentence-transformers generating 384-dim normalized vector embeddings."),
        ("Vector Search Index", "FAISS IndexFlatIP indexing semantic chunks for sub-millisecond similarity search.")
    ], border_accent=ACCENT_CYAN)

    set_notes(s3, """
TALKING POINTS:
"Notice the clean separation in our topology. On the left: a modern React 18 single-page application.
In the center: FastAPI orchestrating transcription, LLM extraction, and transaction verification.
On the right: our dual-store persistence engine. Notice that SQLite is the mutable system of record, while FAISS is the immutable semantic search index. This separation is fundamental to our system's reliability."
""")

    # =========================================================================
    # SLIDE 4: Audio Ingestion & Transcription Engine
    # =========================================================================
    s4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s4)
    add_header(s4, "Ingestion Pipeline", "Speech Processing with faster-whisper",
               "Turning raw conversational audio into time-synchronized acoustic transcripts")

    add_card(s4, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Audio Ingestion & Formats", [
        ("Multi-Format Flexibility", "Accepts standard enterprise formats: MP3, WAV, M4A, and MP4 audio tracks."),
        ("Dual Ingestion Modes", "File upload (drag & drop) or direct browser microphone capture via MediaRecorder API."),
        ("Safe File Handling", "Streams binary audio to backend data/recordings/ directory with sanitized unique filenames."),
        ("Client-Side Visualizer", "Live recording timer and state feedback to prevent empty audio submissions."),
        ("MIME-Type Validation", "Strict server-side validation rejecting invalid or corrupted payloads before pipeline entry.")
    ])

    add_card(s4, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "faster-whisper Acoustic Decoding", [
        ("CTranslate2 Optimization", "Uses faster-whisper (CTranslate2 reimplementation), providing 4x speedup over OpenAI whisper-python with lower VRAM/RAM footprint."),
        ("Model Tier Selection", "Defaulting to base or small model for fast CPU/GPU inference without cloud audio upload fees."),
        ("Segment-Level Timestamps", "Every speech segment is tagged with precise start_time and end_time (seconds)."),
        ("Downstream Traceability", "Timestamps flow into SQLite transcript_segments and vector store metadata, allowing any extracted action item or decision to link back to exact speech moments.")
    ], border_accent=ACCENT_INDIGO)

    set_notes(s4, """
TALKING POINTS:
"Step 1 of the intelligence pipeline is transcription.
We chose faster-whisper, an implementation based on CTranslate2. It is up to 4 times faster than standard Whisper while maintaining identical transcription accuracy.
Crucially, every single sentence is timestamped down to the fraction of a second. This allows our entire system to provide verifiable source citations."
""")

    # =========================================================================
    # SLIDE 5: Structured Intelligence Extraction
    # =========================================================================
    s5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s5)
    add_header(s5, "AI Intelligence Layer", "Structured Extraction via Groq & Pydantic",
               "Eliminating hallucinations through schema-constrained LLM JSON inference")

    add_card(s5, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Extraction Methodology", [
        ("Ultra-Low Latency Inference", "Powered by Groq's LPU architecture (openai/gpt-oss-20b or Llama-3), generating structured intelligence in 1-3 seconds."),
        ("Enforced JSON Schema", "Uses response_format={'type': 'json_object'} to guarantee valid machine-readable JSON on every inference pass."),
        ("Strict System Prompting", "Instructs model to extract strictly verifiable facts from transcript segments, penalizing speculative fabrications."),
        ("Pydantic Validation", "Pydantic models (MeetingIntelligence, ActionItem, Decision, Risk) validate incoming payloads before database persistence.")
    ], border_accent=ACCENT_CYAN)

    add_card(s5, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "Extracted Intelligence Entities", [
        ("Executive Summary", "Curated bullet points capturing strategic meeting themes and core discussion arcs."),
        ("Action Items", "Task description, suggested owner, extracted due date, confidence score (0.0-1.0), and timestamp."),
        ("Meeting Requests", "Topic, proposed date, proposed time, and source timestamp for suggested follow-up syncs."),
        ("Decisions & Consensus", "Explicit business and technical agreements reached during the meeting."),
        ("Risks & Blockers", "Threats to delivery, dependencies, or reliability flagged by participants.")
    ], border_accent=ACCENT_INDIGO)

    set_notes(s5, """
TALKING POINTS:
"Raw transcripts are too long for executives to read.
We send the complete timestamped transcript to Groq's high-speed inference engine. By constraining the model with strict Pydantic schemas and JSON Mode, we extract 5 distinct intelligence entities:
Summaries, Action Items, Meeting Requests, Decisions, and Risks.
Notice that the AI does NOT confirm actions—it marks them as 'pending_review'."
""")

    # =========================================================================
    # SLIDE 6: The Dual-Store Paradigm: SQLite vs FAISS
    # =========================================================================
    s6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s6)
    add_header(s6, "Data Architecture", "The Dual-Store Paradigm: SQLite vs. FAISS",
               "Why structured state and unstructured semantic evidence must never be conflated")

    add_card(s6, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "SQLite: The Mutable State of Record", [
        ("Operational System of Record", "Stores current structured state: meeting metadata, action items, owner emails, calendar events, and decisions."),
        ("Human Edits & Lifecycle", "Administrators can edit tasks, reassign owners, update due dates, and confirm or dismiss items."),
        ("ACID Transactions", "Guarantees reliable writes, foreign key relationships, and atomic status transitions."),
        ("Audit History Tracking", "Every human alteration triggers an immutable delta entry in action_item_history.")
    ], border_accent=ACCENT_EMERALD)

    add_card(s6, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "FAISS: The Immutable Evidence Index", [
        ("Acoustic Truth Index", "Indexes raw, unedited transcript chunks along with meeting IDs and exact timestamps."),
        ("Source Integrity Rule", "Human edits to action items or calendar records NEVER mutate FAISS chunks. FAISS preserves what was actually said."),
        ("Sub-Millisecond Vector Search", "Inner-Product similarity indexing over 384-dimensional dense vectors for semantic queries."),
        ("Zero Drift Guarantee", "Separating evidence from workflow prevents hallucination feedback loops in semantic search and RAG.")
    ], border_accent=ACCENT_INDIGO)

    set_notes(s6, """
TALKING POINTS:
"This slide represents one of our most important architectural decisions.
Many naive AI apps overwrite their vector databases when a user edits an action item. That is a major anti-pattern.
In our system: FAISS represents historical evidence—what was actually spoken in the room. SQLite represents operational truth—current state, reassignments, and authorizations.
Human edits in SQLite never tamper with the FAISS evidence index."
""")

    # =========================================================================
    # SLIDE 7: Action Item Lifecycle & Human-in-the-Loop Governance
    # =========================================================================
    s7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s7)
    add_header(s7, "Governance Model", "Action Item Lifecycle & Audit-Grade History",
               "Full human-in-the-loop control with field-level change tracking")

    add_card(s7, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Stage 1: AI Detection", [
        ("Auto-Categorization", "Items initialized with status = pending_review and confidence score."),
        ("Metadata Parsing", "AI extracts task name, proposed owner, and natural-language due date."),
        ("Zero Side-Effects", "No emails sent, no external state changed without human intervention.")
    ], border_accent=ACCENT_AMBER)

    add_card(s7, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "Stage 2: Human Refinement", [
        ("Per-Item Inline Editing", "Admin can edit Task, Owner, Owner Email, and Due Date directly on the card."),
        ("Pending State Preserved", "Saving an edit does NOT auto-confirm. It persists to SQLite and remains pending review."),
        ("Audit History Insertion", "Every changed field inserts an entry into action_item_history (old_val -> new_val)."),
        ("human_modified Flag", "Item is permanently tagged with human_modified = 1 and updated_at timestamp.")
    ], border_accent=ACCENT_CYAN)

    add_card(s7, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "Stage 3: Explicit Confirmation", [
        ("Independent Authorization", "Admin explicitly clicks 'Confirm' when satisfied with assigned task and owner email."),
        ("State Transition", "Status transitions to confirmed; item immediately surfaces on the Tasks board."),
        ("Event Dispatch", "Triggers transactional email dispatch if owner_email is configured and email_sent = 0."),
        ("Reopen & Revert Support", "Confirmed/Dismissed items can be reopened back to pending_review at any time.")
    ], border_accent=ACCENT_EMERALD)

    set_notes(s7, """
TALKING POINTS:
"Let's look at how action items move through our system.
The AI is strictly an assistant, never an autonomous decision-maker.
When an action is extracted, it enters Stage 1: Pending Review.
In Stage 2, the team lead or admin can edit the task description, specify the exact owner email, and adjust due dates. Every single keystroke is logged in the action_item_history table.
Only in Stage 3 does the human click 'Confirm'."
""")

    # =========================================================================
    # SLIDE 8: Automated Notification Engine & Deduplication
    # =========================================================================
    s8 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s8)
    add_header(s8, "Notification Service", "Automated Transactional Email & Deduplication",
               "Standard-library SMTP notifications with strict confirmation guarantees")

    add_card(s8, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Transactional Dispatch Rules", [
        ("Commit-First Safety", "Email is attempted ONLY AFTER the SQLite transaction successfully commits status = 'confirmed'."),
        ("Direct UI Email Binding", "Recipient address is pulled directly from the action item's owner_email field entered in the UI."),
        ("Zero-Dependency SMTP", "Built using Python's standard library smtplib and email.mime—no heavy n8n or SaaS webhooks needed."),
        ("Non-Blocking Fault Tolerance", "If SMTP credentials are missing or network times out, the task confirmation remains intact and an error is logged."),
        ("Plain-Text Clarity", "Delivers clean, clutter-free emails showing Task, Due Date, and Originating Meeting filename.")
    ], border_accent=ACCENT_INDIGO)

    add_card(s8, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "Deduplication & Reopen Protection", [
        ("The Duplicate Spam Danger", "In real workflows, an admin might confirm an item, realize a typo, reopen it, edit it, and re-confirm. A naive system sends duplicate emails."),
        ("Database Flag: email_sent", "Every action item tracks email_sent INTEGER DEFAULT 0."),
        ("First Confirmation", "Upon first confirm with owner_email, email dispatches; on SMTP success, email_sent is updated to 1."),
        ("Subsequent Re-Confirmations", "If item is reopened and confirmed again, the backend checks email_sent == 1 and skips duplicate dispatch."),
        ("Clean .env Configuration", "Only standard SMTP variables (HOST, PORT, USER, PASSWORD, FROM) reside in environment.")
    ], border_accent=ACCENT_EMERALD)

    set_notes(s8, """
TALKING POINTS:
"Our email service demonstrates our engineering philosophy: reliability over complexity.
We use Python's built-in smtplib—zero third-party dependencies like SendGrid or n8n required.
Most importantly, we have built-in deduplication. If a manager confirms an item, reopens it to fix a detail, and re-confirms, our system will NOT spam the assignee's inbox a second time."
""")

    # =========================================================================
    # SLIDE 9: Internal Event Schedule & Dual Calendar System
    # =========================================================================
    s9 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s9)
    add_header(s9, "Calendar & Scheduling", "Dual-Source Internal Event Management",
               "Bridging AI-suggested follow-ups with manually authorized calendar commitments")

    add_card(s9, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "AI-Detected Meeting Requests", [
        ("Source Table: meeting_requests", "Populated automatically during transcription analysis when participants discuss future meetings."),
        ("Verbatim Date Preservation", "Stores dates and times exactly as uttered (e.g., 'Next Wednesday', 'Sept 20 at 3 PM') without date hallucination."),
        ("Review & Authorization Flow", "Requests sit in Pending Review until confirmed or dismissed by the user."),
        ("In-Place Editing", "Admins can refine topics, dates, and times before confirming."),
        ("Originating Meeting Link", "Every request displays a direct link back to the source meeting transcript.")
    ], border_accent=ACCENT_AMBER)

    add_card(s9, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "Manual Event Creation (calendar_events)", [
        ("Source Table: calendar_events", "Dedicated table for human-scheduled events, keeping AI suggestions completely separated."),
        ("Immediate Confirmation", "Manually created events are confirmed on creation (source = 'manual', status = 'confirmed')."),
        ("Clean '+ Add Event' Modal", "Intuitive modal capturing Title (required), Event Date (required), Time, and Notes."),
        ("Full CRUD Lifecycle", "Endpoints for POST /calendar/events, PATCH /calendar/events/{id}, and DELETE /calendar/events/{id}."),
        ("Visual Differentiation", "Calendar UI clearly badges items as 'AI Suggested' vs. 'Manually Created'.")
    ], border_accent=ACCENT_INDIGO)

    set_notes(s9, """
TALKING POINTS:
"Slide 9 highlights our Calendar architecture.
Again, this is not Google Calendar or Outlook—it is an internal meeting intelligence schedule.
We support two distinct sources:
On the left: AI-detected requests from transcripts that need triage.
On the right: Manually created events with full edit and delete capabilities.
Both live harmoniously on the same Calendar page with clear visual badges."
""")

    # =========================================================================
    # SLIDE 10: Semantic Vector Search Architecture (FAISS)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s10)
    add_header(s10, "Neural Search Engine", "Semantic Retrieval with Sentence-Transformers & FAISS",
               "Finding meeting context by conceptual meaning rather than brittle keyword matching")

    add_card(s10, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Embedding & Chunking Pipeline", [
        ("Segment Aggregation", "Raw transcript segments are concatenated and divided into character chunks (~250 chars) with timestamp boundaries."),
        ("Dense Representation", "Embedded locally using sentence-transformers (all-MiniLM-L6-v2), producing 384-dimensional dense vectors."),
        ("L2 Normalization", "All embedding vectors are L2-normalized so that inner-product operations equal cosine similarity."),
        ("Metadata Mapping", "A companion metadata.json links every vector ID to meeting_id, start_time, end_time, and verbatim segment text.")
    ], border_accent=ACCENT_CYAN)

    add_card(s10, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "FAISS Index & Search Capabilities", [
        ("IndexFlatIP Core", "In-memory FAISS flat inner-product index providing exact top-k nearest neighbor retrieval in <2ms."),
        ("Automated Re-Indexing", "Whenever a new meeting is processed, indexer.py rebuilds the index across all stored meetings in one pass."),
        ("Conceptual Discovery", "Queries like 'infrastructure bottlenecks' retrieve discussions about 'Kubernetes memory leaks' even without exact word overlap."),
        ("Confidence Scoring", "Returns similarity scores and exact timestamp badges directly in the frontend Search interface.")
    ], border_accent=ACCENT_INDIGO)

    set_notes(s10, """
TALKING POINTS:
"What happens when you need to find something said three months ago?
Traditional keyword search fails if you search for 'budget constraints' but the speaker said 'we are burning too much cash'.
With our FAISS and Sentence-Transformers vector engine, queries search semantic meaning.
The index maps directly to exact timestamps, so you can jump straight to the spoken quote."
""")

    # =========================================================================
    # SLIDE 11: Retrieval-Augmented Generation (RAG) & "Ask AI"
    # =========================================================================
    s11 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s11)
    add_header(s11, "Grounded RAG Assistant", "Conversational Q&A Grounded in Transcript Evidence",
               "Direct answers with verifiable source attribution and strict anti-hallucination guardrails")

    add_card(s11, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "The RAG Execution Flow", [
        ("Step 1: User Query", "User submits a natural-language question (e.g., 'What did Sarah commit to regarding the launch date?')."),
        ("Step 2: Vector Search", "Backend embeds query and queries FAISS to retrieve top-5 most relevant transcript chunks."),
        ("Step 3: Context Assembly", "Formatted meeting sources with IDs and timestamps are injected into the prompt."),
        ("Step 4: Constrained Synthesis", "Groq LLM synthesizes an evidence-bound direct answer referencing the provided snippets."),
        ("Step 5: Source Attribution", "Frontend displays the concise answer alongside expandable source cards showing exact speaker quotes.")
    ], border_accent=ACCENT_CYAN)

    add_card(s11, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "Guardrails & Anti-Hallucination Rules", [
        ("Strict Grounding Rule", "The model prompt enforces: 'Answer using ONLY the provided meeting evidence. If sources do not contain enough information, state that clearly.'"),
        ("Zero Fabrication Policy", "Temperature is set to 0.0 for deterministic, fact-bound responses without creative embellishment."),
        ("Cross-Meeting Synthesis", "The RAG assistant can link related discussion points across different meetings held weeks apart."),
        ("Auditable Trust", "Every response is accompanied by segment IDs and start/end timestamps for instantaneous peer verification.")
    ], border_accent=ACCENT_EMERALD)

    set_notes(s11, """
TALKING POINTS:
"Our 'Ask AI' feature takes vector search to the next level with Retrieval-Augmented Generation.
Instead of forcing users to read five different transcripts, the assistant compiles a direct answer.
Crucially, look at our guardrails: Temperature is set to zero, and the system prompt explicitly forbids speculation. If the answer wasn't said in a meeting, it will tell you."
""")

    # =========================================================================
    # SLIDE 12: Frontend Architecture & User Experience
    # =========================================================================
    s12 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s12)
    add_header(s12, "Frontend UX", "Enterprise Single-Page Application (React 18 + Vite)",
               "Consistent dark enterprise design system tailored for high-density information review")

    add_card(s12, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Design Language", [
        ("Unified SaaS Aesthetic", "Slate-950 background, slate-900 elevated cards, and restrained slate-800 borders."),
        ("Consistent Semantic Badges", "Emerald for Confirmed, Amber for Pending, Slate for Dismissed, Indigo for AI/Human tags."),
        ("Zero Layout Shift", "Instant client-side routing via React Router DOM with persistent Sidebar navigation."),
        ("No Third-Party Bloat", "Clean Tailwind CSS styling without bulky UI component library overhead.")
    ])

    add_card(s12, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "Key Application Pages", [
        ("Dashboard", "Executive metrics (Meetings, Pending, Tasks, Decisions) and recent meetings summary list."),
        ("Assistant Hub", "Dual audio ingestion: drag-and-drop file upload & live mic recording with visual timer."),
        ("Meeting Intelligence", "Tabbed deep dive (Overview, Transcript, Actions, Decisions, Risks, and Ask AI drawer)."),
        ("Review Inbox", "Rapid triage queue for pending action items across all analyzed recordings.")
    ], border_accent=ACCENT_INDIGO)

    add_card(s12, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "Dedicated Workspaces", [
        ("Tasks Page (/tasks)", "Confirmed actionable commitments with owner badges, due dates, and source meeting links."),
        ("Calendar Page (/calendar)", "Split-view managing Confirmed Events alongside Pending Review requests with '+ Add Event' modal."),
        ("Decisions Repository", "Aggregated catalog of all business and architectural decisions captured."),
        ("Semantic Search (/search)", "Instant vector search interface with real-time query results and score ranking.")
    ], border_accent=ACCENT_CYAN)

    set_notes(s12, """
TALKING POINTS:
"Turning to the frontend: We built an interface that looks and feels like a tier-one enterprise SaaS product.
Everything uses a restrained dark slate palette designed for long reading sessions.
Pages are divided into operational workflows: Executive Dashboard, Ingestion Assistant, Deep-Dive Meeting View, Tasks Board, and the Dual Calendar."
""")

    # =========================================================================
    # SLIDE 13: Data Integrity, Migrations & Privacy
    # =========================================================================
    s13 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s13)
    add_header(s13, "Data Governance", "Schema Migrations, Audit Trails & Privacy First",
               "Protecting data permanence and confidentiality across software versions")

    add_card(s13, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Safe SQLite Schema Migrations", [
        ("PRAGMA table_info Inspection", "Database migrations dynamically inspect table schema columns before executing ALTER TABLE."),
        ("No Destructive Commands", "Never drops or recreates tables; existing production databases survive software upgrades seamlessly."),
        ("Idempotent Startup Routine", "migrate_database() runs automatically on server launch, ensuring backwards-compatible column additions."),
        ("Graceful Nullability", "New fields like owner_email and updated_at are nullable, ensuring zero migration errors on legacy records.")
    ], border_accent=ACCENT_EMERALD)

    add_card(s13, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.8), "Enterprise Privacy & Governance", [
        ("Local Acoustic Processing", "Speech transcription runs locally via faster-whisper; raw audio is never transmitted to cloud transcription APIs."),
        ("Local Vector Storage", "FAISS embeddings and indexes remain entirely on-premises inside the local file system."),
        ("Field-Level Audit Trail", "action_item_history tracks exactly what was changed, the old value, the new value, and the timestamp."),
        ("Zero Credential Leakage", "No hardcoded passwords or API keys; all sensitive tokens managed via clean .env variables.")
    ], border_accent=ACCENT_INDIGO)

    set_notes(s13, """
TALKING POINTS:
"In any enterprise AI project, data governance is paramount.
First: Our migrations are completely safe. We use PRAGMA table_info to conditionally alter tables, meaning you will never lose existing meeting data during updates.
Second: Privacy. We run speech recognition and vector storage locally. Only the sanitized transcript text passes through Groq for inference."
""")

    # =========================================================================
    # SLIDE 14: Step-by-Step Live Demo Walkthrough
    # =========================================================================
    s14 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s14)
    add_header(s14, "Product Demonstration", "Recommended Step-by-Step Live Demo Script",
               "A structured 5-stage script to showcase the companion during customer or team demos")

    add_card(s14, Inches(0.8), Inches(2.0), Inches(5.6), Inches(2.3), "Phase 1: Ingestion & Analysis", [
        ("Navigate to /assistant", "Upload sample audio (or record live microphone test)."),
        ("Trigger Analysis", "Show status progression: Uploading -> Transcribing -> Extracting Intelligence -> Rebuilding Index."),
        ("Highlight Speed", "Point out sub-10 second turnaround from audio to complete intelligence.")
    ], border_accent=ACCENT_CYAN)

    add_card(s14, Inches(6.8), Inches(2.0), Inches(5.7), Inches(2.3), "Phase 2: Meeting Deep-Dive", [
        ("Review Extracted Entities", "Walk through Executive Summary, Decisions, and Risks."),
        ("Inspect Transcript Sync", "Show timestamped transcript segments linking to source audio."),
        ("Test Q&A Panel", "Ask a question in the 'Ask AI' drawer and highlight source citations.")
    ], border_accent=ACCENT_INDIGO)

    add_card(s14, Inches(0.8), Inches(4.5), Inches(5.6), Inches(2.4), "Phase 3: Human-in-the-Loop Action Editing", [
        ("Click Inline Edit", "Edit task description, assign owner, and add owner email."),
        ("Save & Verify Status", "Point out item remains 'Pending Review' and is tagged 'Edited by human'."),
        ("Confirm Task", "Click Confirm -> show status shift to 'Confirmed' and email dispatch."),
        ("Verify on /tasks", "Navigate to Tasks page to see confirmed item immediately listed.")
    ], border_accent=ACCENT_EMERALD)

    add_card(s14, Inches(6.8), Inches(4.5), Inches(5.7), Inches(2.4), "Phase 4 & 5: Calendar & Semantic Search", [
        ("Calendar Triaging", "Confirm an AI meeting request on /calendar."),
        ("Manual Event Creation", "Click '+ Add Event', create a custom event, and observe immediate confirmed listing."),
        ("Semantic Discovery", "Navigate to /search, type a conceptual query, and show instant ranked transcript results.")
    ], border_accent=ACCENT_AMBER)

    set_notes(s14, """
SPEAKER DEMO SCRIPT:
"Here is the exact 5-minute live demonstration flow:
Start on Assistant: Drag in a 2-minute audio recording.
Show the processing pipeline: In seconds, you land on the Meeting Intelligence page.
Walk through the tabs: Point out the summary, decisions, and risks.
Demonstrate human governance: Edit an action item, add your email, click save—notice it's still pending. Then click Confirm!
Jump to Tasks to show it appeared.
Finally, go to Calendar: Show the AI follow-up requests and click '+ Add Event' to create a manual event. That's the complete loop!"
""")

    # =========================================================================
    # SLIDE 15: Engineering Decisions & Technical Trade-Offs
    # =========================================================================
    s15 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s15)
    add_header(s15, "Engineering Rationale", "Core Technical Decisions & Strategic Trade-Offs",
               "Why we prioritized simplicity, determinism, and minimal dependencies over complexity")

    add_card(s15, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Storage: SQLite vs. Postgres", [
        ("Why SQLite Won", "Zero configuration, single-file portability, embedded in-process execution, and instant backups."),
        ("Concurrency Fit", "Our write model is transactional per-meeting and human-paced; SQLite handles hundreds of reads/sec effortlessly."),
        ("Simplicity Principle", "Avoided running external database containers or managing connection pools for an internal tool.")
    ], border_accent=ACCENT_INDIGO)

    add_card(s15, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "Inference: Groq vs. Self-Hosted", [
        ("Why Groq Won", "Sub-second LPU throughput allows synchronous meeting analysis without background Celery worker complexity."),
        ("Cost Efficiency", "Pay-per-token JSON mode API eliminates the need for expensive dedicated GPU instances on standby."),
        ("Zero Cold Starts", "Instant API availability compared to spinning up local 70B parameter models on developer machines.")
    ], border_accent=ACCENT_CYAN)

    add_card(s15, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "Vector: FAISS vs. Managed Vector DBs", [
        ("Why FAISS Won", "Runs fully in-memory locally, saving index to disk in milliseconds without Pinecone/Weaviate SaaS fees."),
        ("Direct Acoustic Link", "Metadata ties directly into local SQLite row IDs and timestamp offsets without network roundtrips."),
        ("Predictable Determinism", "Flat inner product provides exact nearest neighbors with zero indexing latency.")
    ], border_accent=ACCENT_EMERALD)

    set_notes(s15, """
TALKING POINTS:
"Engineers often ask why we didn't use Postgres, Kafka, or Pinecone.
Our answer is deliberate: We chose the simplest robust architecture that delivers the required performance.
SQLite running in WAL mode is blisteringly fast. FAISS runs directly in RAM. Groq gives us 500 tokens per second.
The result is a system you can clone and run in 60 seconds with zero cloud infrastructure overhead."
""")

    # =========================================================================
    # SLIDE 16: Roadmap & Future Horizons
    # =========================================================================
    s16 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(s16)
    add_header(s16, "Future Horizons", "Product Roadmap & Extensibility Paths",
               "Strategic evolution from standalone companion to ubiquitous intelligence layer")

    add_card(s16, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "Phase 1: Ecosystem Integration", [
        ("Enterprise Calendar Sync", "Bi-directional CalDAV / Google Calendar / Microsoft Graph integration for confirmed events."),
        ("Direct Issue Sync", "One-click export of confirmed tasks to GitHub Issues, Jira, or Linear via lightweight webhooks."),
        ("Chat Platform Bots", "Slack and Microsoft Teams bots for automated intelligence delivery and Slack-based task confirmation.")
    ], border_accent=ACCENT_INDIGO)

    add_card(s16, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "Phase 2: Acoustic Intelligence", [
        ("Speaker Diarization", "Integrating PyAnnote / WhisperX to automatically label participant voices (e.g. 'Speaker 1 = Alex')."),
        ("Sentiment & Tension Detection", "Highlighting moments of high disagreement or excitement in meeting timelines."),
        ("Live Audio Streaming", "Real-time WebSocket audio streaming for live transcription and running meeting timers.")
    ], border_accent=ACCENT_CYAN)

    add_card(s16, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "Phase 3: Multi-Meeting Intelligence", [
        ("Project-Level Aggregation", "Tagging meetings by project or sprint for aggregated milestone progress dashboards."),
        ("Automated Weekly Digest", "Generating AI executive briefing summarizing commitments made across all 15 weekly syncs."),
        ("Commitment Fulfillment Tracker", "Tracking whether action items from past meetings were marked completed in subsequent meetings.")
    ], border_accent=ACCENT_EMERALD)

    set_notes(s16, """
TALKING POINTS:
"Looking to the future, our architecture is built to scale:
First: Bi-directional calendar and issue sync with tools like Linear and Jira.
Second: Speaker diarization to automatically detect who said what.
Third: Cross-meeting milestone tracking to automatically check if last week's action items were completed this week.
Thank you! I'm now ready to take any questions or jump into the live product demo."
""")

    # Save presentation
    output_path = os.path.abspath(r"c:\Users\Aditya N\Downloads\projects\businessbuddy\AI_Meeting_Intelligence_Companion_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    create_presentation()
