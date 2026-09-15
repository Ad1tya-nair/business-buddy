import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import { analyzeMeeting } from "../services/api"
import { useAuth } from "../context/AuthContext"


function Assistant() {
  const navigate = useNavigate()
  const { isLead } = useAuth()

  const fileInputRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const timerRef = useRef(null)

  const [mode, setMode] = useState("upload")

  const [selectedFile, setSelectedFile] =
    useState(null)

  const [dragActive, setDragActive] =
    useState(false)

  const [processing, setProcessing] =
    useState(false)

  const [recording, setRecording] =
    useState(false)

  const [recordingSeconds, setRecordingSeconds] =
    useState(0)

  const [error, setError] =
    useState(null)


  // ============================================================
  // FILE SELECTION
  // ============================================================

  function handleFile(file) {
    if (!file) {
      return
    }

    const allowedTypes = [
      "audio/mpeg",
      "audio/mp3",
      "audio/wav",
      "audio/x-wav",
      "audio/mp4",
      "audio/x-m4a",
      "audio/m4a",
    ]

    const extension =
      file.name
        .split(".")
        .pop()
        ?.toLowerCase()

    const allowedExtensions = [
      "mp3",
      "wav",
      "m4a",
    ]

    if (
      !allowedTypes.includes(file.type) &&
      !allowedExtensions.includes(extension)
    ) {
      setError(
        "Please select an MP3, WAV, or M4A audio file."
      )
      return
    }

    setSelectedFile(file)
    setError(null)
  }


  function handleFileInput(event) {
    const file =
      event.target.files?.[0]

    handleFile(file)
  }


  function handleDrop(event) {
    event.preventDefault()

    setDragActive(false)

    const file =
      event.dataTransfer.files?.[0]

    handleFile(file)
  }


  // ============================================================
  // UPLOAD
  // ============================================================

  async function handleUpload() {
    if (!selectedFile || processing) {
      return
    }

    try {
      setProcessing(true)
      setError(null)

      const result =
        await analyzeMeeting(selectedFile)

      navigate(
        `/meetings/${result.meeting_id}`
      )

    } catch (err) {
      setError(
        err.message ||
        "Failed to analyze meeting."
      )
    } finally {
      setProcessing(false)
    }
  }


  // ============================================================
  // RECORDING
  // ============================================================

  async function startRecording() {
    if (recording || processing) {
      return
    }

    try {
      setError(null)

      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error(
          "Your browser does not support microphone recording."
        )
      }

      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        })

      const mimeTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
      ]

      const supportedType =
        mimeTypes.find((type) =>
          MediaRecorder.isTypeSupported(type)
        )

      const recorder =
        supportedType
          ? new MediaRecorder(
              stream,
              {
                mimeType:
                  supportedType,
              }
            )
          : new MediaRecorder(stream)

      audioChunksRef.current = []

      recorder.ondataavailable =
        (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(
              event.data
            )
          }
        }

      recorder.onstop =
        async () => {
          stream
            .getTracks()
            .forEach((track) =>
              track.stop()
            )

          clearInterval(
            timerRef.current
          )

          setRecording(false)

          const blob =
            new Blob(
              audioChunksRef.current,
              {
                type:
                  recorder.mimeType ||
                  "audio/webm",
              }
            )

          if (blob.size === 0) {
            setError(
              "No audio was recorded."
            )
            return
          }

          const extension =
            recorder.mimeType.includes("ogg")
              ? "ogg"
              : "webm"

          const file =
            new File(
              [blob],
              `live-meeting-${Date.now()}.${extension}`,
              {
                type:
                  recorder.mimeType ||
                  "audio/webm",
              }
            )

          try {
            setProcessing(true)

            const result =
              await analyzeMeeting(file)

            navigate(
              `/meetings/${result.meeting_id}`
            )

          } catch (err) {
            setError(
              err.message ||
              "Failed to analyze recording."
            )
          } finally {
            setProcessing(false)
          }
        }

      mediaRecorderRef.current =
        recorder

      setRecordingSeconds(0)

      timerRef.current =
        setInterval(() => {
          setRecordingSeconds(
            (previous) =>
              previous + 1
          )
        }, 1000)

      recorder.start()

      setRecording(true)

    } catch (err) {
      setError(
        err.message ||
        "Microphone access was not available."
      )
    }
  }


  function stopRecording() {
    if (
      !mediaRecorderRef.current ||
      mediaRecorderRef.current.state ===
        "inactive"
    ) {
      return
    }

    mediaRecorderRef.current.stop()
  }


  // ============================================================
  // CLEANUP
  // ============================================================

  useEffect(() => {
    return () => {
      clearInterval(timerRef.current)

      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !==
          "inactive"
      ) {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])


  function formatRecordingTime(seconds) {
    const minutes =
      Math.floor(seconds / 60)

    const remaining =
      seconds % 60

    return `${String(minutes).padStart(
      2,
      "0"
    )}:${String(remaining).padStart(
      2,
      "0"
    )}`
  }

  if (!isLead) {
    return (
      <div className="mx-auto max-w-2xl rounded-2xl border border-slate-200/90 bg-white p-10 text-center shadow-xs">
        <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
          Meeting Assistant
        </span>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">
          Meeting ingestion is managed by the Team Lead.
        </h1>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          You can view all processed meetings, transcripts, and structured intelligence on the Meetings page.
        </p>
        <button
          type="button"
          onClick={() => navigate("/meetings")}
          className="mt-6 inline-flex rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700"
        >
          View meetings →
        </button>
      </div>
    )
  }


  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="space-y-8">

      {/* HEADER */}
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
          AI Meeting Intelligence
        </span>

        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
          Assistant
        </h1>

        <p className="mt-1.5 max-w-2xl text-sm leading-6 text-slate-500">
          Upload an audio recording or record a live meeting with your microphone to extract structured intelligence.
        </p>
      </div>


      {/* MODE SELECTOR */}
      <div className="flex max-w-md rounded-2xl border border-slate-300 bg-slate-100 p-1 shadow-2xs">
        <button
          type="button"
          aria-pressed={mode === "upload"}
          onClick={() => {
            if (!recording && !processing) {
              setMode("upload")
              setError(null)
            }
          }}
          className={`flex-1 rounded-xl px-5 py-2.5 text-xs font-semibold transition-all ${
            mode === "upload"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/25"
              : "bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          Upload recording
        </button>

        <button
          type="button"
          aria-pressed={mode === "record"}
          onClick={() => {
            if (!recording && !processing) {
              setMode("record")
              setError(null)
            }
          }}
          className={`flex-1 rounded-xl px-5 py-2.5 text-xs font-semibold transition-all ${
            mode === "record"
              ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/25"
              : "bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          Record live
        </button>
      </div>


      {/* MAIN ASSISTANT CARD */}
      <section className="rounded-2xl border border-slate-200/90 bg-white p-8 shadow-xs">

        {/* UPLOAD MODE */}
        {mode === "upload" && (
          <>
            <div
              onDragOver={(event) => {
                event.preventDefault()
                setDragActive(true)
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => !processing && fileInputRef.current?.click()}
              className={`cursor-pointer rounded-2xl border-2 border-dashed px-8 py-14 text-center transition-all ${
                dragActive
                  ? "border-indigo-500 bg-indigo-50/50"
                  : "border-slate-300 bg-slate-50/50 hover:border-indigo-400 hover:bg-slate-50"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".mp3,.wav,.m4a,audio/mpeg,audio/wav,audio/mp4"
                onChange={handleFileInput}
                className="hidden"
              />

              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-2xl text-indigo-600 font-bold shadow-2xs">
                ↑
              </div>

              <h2 className="mt-4 text-base font-semibold text-slate-900">
                {selectedFile
                  ? selectedFile.name
                  : "Upload a meeting recording"}
              </h2>

              <p className="mt-1.5 text-xs text-slate-500">
                {selectedFile
                  ? `${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`
                  : "Drag and drop an audio file here, or click to browse"}
              </p>

              <span className="mt-3 inline-block rounded-md bg-slate-100 px-2.5 py-0.5 text-[11px] font-medium text-slate-500">
                MP3, WAV, or M4A
              </span>
            </div>

            {selectedFile && !processing && (
              <button
                type="button"
                onClick={handleUpload}
                className="mt-5 w-full rounded-xl bg-indigo-600 px-5 py-3.5 text-sm font-semibold text-white shadow-xs transition hover:bg-indigo-700"
              >
                Analyze meeting →
              </button>
            )}

            {processing && (
              <div className="mt-5 rounded-2xl border border-indigo-100 bg-indigo-50/60 p-6 text-center">
                <p className="text-sm font-semibold text-indigo-900">
                  Analyzing meeting...
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Transcribing the audio locally and extracting structured intelligence with Groq...
                </p>
              </div>
            )}
          </>
        )}


        {/* RECORD MODE */}
        {mode === "record" && (
          <div className="flex flex-col items-center py-8 text-center">
            <div
              className={`flex h-24 w-24 items-center justify-center rounded-full border transition-all ${
                recording
                  ? "border-red-400/50 bg-red-50 ring-8 ring-red-500/10 animate-pulse"
                  : "border-slate-200 bg-slate-100"
              }`}
            >
              <div
                className={`h-8 w-8 rounded-full ${
                  recording ? "bg-red-600" : "bg-slate-400"
                }`}
              />
            </div>

            <h2 className="mt-6 text-xl font-bold text-slate-900">
              {recording
                ? "Assistant is listening"
                : processing
                ? "Processing recording"
                : "Record a live meeting"}
            </h2>

            <p className="mt-1.5 max-w-md text-sm leading-6 text-slate-500">
              {recording
                ? "The assistant is capturing audio through your browser microphone. Stop when finished."
                : processing
                ? "Transcribing the recording and extracting meeting intelligence..."
                : "Use your microphone to capture conversational speech. The recording will be analyzed when you stop."}
            </p>

            {recording && (
              <div className="mt-6">
                <p className="font-mono text-4xl font-bold text-slate-900">
                  {formatRecordingTime(recordingSeconds)}
                </p>
                <p className="mt-1 text-xs font-semibold text-red-600">
                  ● Live Recording Active
                </p>
              </div>
            )}

            {!recording && !processing && (
              <button
                type="button"
                onClick={startRecording}
                className="mt-7 rounded-xl bg-indigo-600 px-8 py-3 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700"
              >
                Start recording
              </button>
            )}

            {recording && (
              <button
                type="button"
                onClick={stopRecording}
                className="mt-7 rounded-xl bg-red-600 px-8 py-3 text-xs font-semibold text-white shadow-xs transition hover:bg-red-700"
              >
                Stop recording
              </button>
            )}

            {processing && (
              <div className="mt-7 rounded-xl border border-indigo-100 bg-indigo-50/60 px-6 py-4 text-xs font-medium text-indigo-900">
                Transcribing and analyzing recording...
              </div>
            )}
          </div>
        )}

      </section>


      {/* ERROR */}
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50/80 p-5 text-sm text-red-700">
          {error}
        </div>
      )}


    </div>
  )
}

export default Assistant