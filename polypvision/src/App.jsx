import React, { useMemo, useState } from 'react';
import {
  Activity,
  ArrowRight,
  Brain,
  Camera,
  CheckCircle2,
  CircleAlert,
  Upload,
  FileVideo2,
  Sparkles,
  ShieldCheck,
  Waves,
  Bot,
  Send,
  Play,
  ScanSearch,
  Layers3,
  LogOut,
  Stethoscope,
  BadgeInfo,
  AlertTriangle,
} from 'lucide-react';

function Chip({ children }) {
  return (
    <span className="inline-flex items-center rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 shadow-sm">
      {children}
    </span>
  );
}

function Panel({ title, icon: Icon, children, className = '' }) {
  return (
    <div className={`rounded-3xl border border-slate-200 bg-white/90 p-5 shadow-[0_12px_40px_rgba(15,23,42,0.08)] backdrop-blur ${className}`}>
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100">
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      </div>
      {children}
    </div>
  );
}

export default function PolypVisionDashboard() {
  const [page, setPage] = useState('home');
  const [chatInput, setChatInput] = useState('What is the size of the detected polyp?');
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Upload a video to begin analysis.' },
  ]);
  const [selectedKF, setSelectedKF] = useState(null);

  const summary = useMemo(
    () => ({
      uniquePolyps: 2,
      framesProcessed: 186,
      confidence: '0.94',
      largestPolyp: '12.4 mm',
      bboxCount: 14,
    }),
    []
  );

  const keyframes = useMemo(() => {
    const data = [
      { id: 'ID 01', frame: 42, area: 1500, confidence: 0.97, bbox: '120×75 px', severity: 'High' },
      { id: 'ID 02', frame: 87, area: 900, confidence: 0.92, bbox: '88×60 px', severity: 'Medium' },
      { id: 'ID 03', frame: 133, area: 500, confidence: 0.88, bbox: '61×48 px', severity: 'Low' },
    ];
    return data.sort((a, b) => b.area - a.area);
  }, []);

  const maxArea = keyframes[0]?.area ?? 1;

  const getColor = (area) => {
    const ratio = area / maxArea;
    if (ratio > 0.72) return 'border-red-500 bg-red-50';
    if (ratio > 0.42) return 'border-yellow-400 bg-yellow-50';
    return 'border-emerald-400 bg-emerald-50';
  };

  const handleSend = () => {
    if (!chatInput.trim()) return;
    const question = chatInput.trim();
    let reply = '⚠️ This is an AI-assisted demo. Please do not rely on it alone for medical decisions.';
    if (/how many|count/i.test(question)) reply = `There are ${summary.uniquePolyps} unique polyps detected across the video.`;
    else if (/size/i.test(question)) reply = `The largest detected polyp is approximately ${summary.largestPolyp}.`;
    else if (/present|there is|is there|exist/i.test(question)) reply = 'Yes, a polyp is present in the uploaded video with high confidence.';
    else if (/what should i do|next|can be done/i.test(question)) reply = 'This system can help summarize findings, highlight keyframes, and guide you to consult a gastroenterologist for next steps.';
    else if (/precaution|care|avoid/i.test(question)) reply = 'Avoid delays in clinical follow-up, and do not treat the AI output as a final diagnosis.';
    else if (/frame/i.test(question)) reply = 'The most confident detections occur around frames 42, 87, and 133.';

    setMessages((prev) => [...prev, { role: 'user', text: question }, { role: 'assistant', text: reply }]);
    setChatInput('');
  };

  if (page === 'home') {
    return (
      <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(16,185,129,0.18),_transparent_35%),linear-gradient(180deg,#f8fffc_0%,#eef7f3_100%)] text-slate-900">
        <div className="mx-auto flex min-h-screen max-w-7xl items-center px-6 py-10">
          <div className="grid w-full grid-cols-1 overflow-hidden rounded-[2rem] border border-white/60 bg-white/65 shadow-[0_30px_120px_rgba(15,23,42,0.12)] backdrop-blur-xl lg:grid-cols-2">
            <div className="relative hidden min-h-[760px] overflow-hidden p-10 lg:block">
              <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(16,185,129,0.14),rgba(255,255,255,0.2))]" />
              <div className="absolute -right-20 -top-24 h-72 w-72 rounded-full bg-emerald-200/60 blur-3xl" />
              <div className="absolute -bottom-24 -left-20 h-72 w-72 rounded-full bg-cyan-200/60 blur-3xl" />
              <div className="relative z-10 flex h-full flex-col justify-between">
                <div>
                  <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/80 px-4 py-2 text-sm font-medium text-emerald-700 ring-1 ring-emerald-100">
                    <Stethoscope className="h-4 w-4" />
                    PolypVision | Colonoscopy AI Assistant
                  </div>
                  <h1 className="max-w-xl text-5xl font-bold tracking-tight text-slate-900">
                    Smart colonoscopy review with detection, segmentation, and a medical VLM.
                  </h1>
                  <p className="mt-5 max-w-lg text-lg leading-8 text-slate-600">
                    A clean health-tech dashboard: view bounding boxes, segmented output, keyframes, and ask polyp-related questions in natural language.
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {[
                    ['Real-time analysis', 'YOLO + Polyp-PVT pipeline'],
                    ['Unique polyp count', 'Tracking-enabled summary'],
                    ['Medical VLM chat', 'Ask follow-up questions'],
                    ['Clinical-ready UI', 'Polished presentation mode'],
                  ].map(([a, b]) => (
                    <div key={a} className="rounded-3xl border border-white/70 bg-white/70 p-4 shadow-sm">
                      <div className="text-sm font-semibold text-slate-900">{a}</div>
                      <div className="mt-1 text-sm text-slate-600">{b}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex min-h-[760px] items-center p-6 sm:p-10">
              <div className="w-full">
                <div className="mb-6 flex items-center gap-3 lg:hidden">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-white shadow-lg shadow-emerald-200">
                    <Activity className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="text-xl font-bold">PolypVision</div>
                    <div className="text-sm text-slate-500">Colonoscopy AI Assistant</div>
                  </div>
                </div>

                <div className="mb-8">
                  <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 ring-1 ring-emerald-100">
                    <ShieldCheck className="h-4 w-4" />
                    Demo access
                  </div>
                  <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900">Enter the dashboard</h2>
                  <p className="mt-2 max-w-md text-slate-600">No login needed. Continue directly to the analysis workspace.</p>
                </div>

                <div className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700">Project name</label>
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-400">PolypVision</div>
                  </div>
                  <button
                    onClick={() => setPage('results')}
                    className="group inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-5 py-3.5 font-semibold text-white shadow-lg shadow-emerald-200 transition hover:-translate-y-0.5 hover:bg-emerald-700"
                  >
                    Open Analysis Workspace <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                  </button>
                </div>

                <div className="mt-6 flex items-center gap-3 text-sm text-slate-500">
                  <CircleAlert className="h-4 w-4 text-amber-500" />
                  Results shown in the next screen can be hardcoded for presentation.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[linear-gradient(180deg,#f7fffb_0%,#eef6f1_100%)] text-slate-900">
      <div className="mx-auto max-w-[1600px] px-4 py-4 sm:px-6 lg:px-8">
        <div className="mb-4 flex items-center justify-between rounded-3xl border border-white/60 bg-white/80 px-5 py-4 shadow-[0_10px_40px_rgba(15,23,42,0.08)] backdrop-blur">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-600 text-white shadow-lg shadow-emerald-200">
              <Activity className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight sm:text-2xl">PolypVision</h1>
                <Chip>Clinical AI Demo</Chip>
              </div>
              <div className="text-sm text-slate-500">Detection • Segmentation • Tracking • VLM assistant</div>
            </div>
          </div>
          <button
            onClick={() => setPage('home')}
            className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 transition hover:border-emerald-200 hover:text-emerald-700"
          >
            <LogOut className="h-4 w-4" /> Back
          </button>
        </div>

        <div className="grid gap-4 xl:grid-cols-[1.4fr_0.9fr]">
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-4">
              <Panel title="Unique Polyps" icon={ScanSearch}>
                <div className="text-3xl font-bold text-slate-900">{summary.uniquePolyps}</div>
                <div className="mt-1 text-sm text-slate-500">Tracked across the video</div>
              </Panel>
              <Panel title="Frames Processed" icon={FileVideo2}>
                <div className="text-3xl font-bold text-slate-900">{summary.framesProcessed}</div>
                <div className="mt-1 text-sm text-slate-500">Video analysis complete</div>
              </Panel>
              <Panel title="Confidence" icon={ShieldCheck}>
                <div className="text-3xl font-bold text-slate-900">{summary.confidence}</div>
                <div className="mt-1 text-sm text-slate-500">Average detection score</div>
              </Panel>
              <Panel title="Largest Polyp" icon={Layers3}>
                <div className="text-3xl font-bold text-slate-900">{summary.largestPolyp}</div>
                <div className="mt-1 text-sm text-slate-500">Estimated from mask area</div>
              </Panel>
            </div>

            <Panel title="Case Upload" icon={Upload}>
              <div className="flex flex-wrap gap-3 items-center">
                <button className="inline-flex items-center gap-2 rounded-2xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-200">
                  <FileVideo2 className="h-4 w-4" /> Upload Video
                </button>
                <div className="ml-auto inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-xs font-medium text-slate-600">
                  <BadgeInfo className="h-3.5 w-3.5" /> Results are mocked for now
                </div>
              </div>

              <div className="mt-5 grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
                <div className="overflow-hidden rounded-3xl border border-slate-200 bg-slate-950 p-4 shadow-inner">
                  <div className="mb-3 flex items-center justify-between text-xs text-slate-300">
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-3 py-1 text-emerald-200">
                      <Play className="h-3.5 w-3.5" /> Video Preview
                    </span>
                    <span>Patient • Session 01</span>
                  </div>
                  <div className="relative aspect-video overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950">
                    <div className="absolute inset-0">
                      <div className="absolute left-8 top-12 h-28 w-44 rounded-[2rem] border-2 border-emerald-400" />
                      <div className="absolute left-44 top-24 h-24 w-36 rounded-[2rem] border-2 border-cyan-300" />
                      <div className="absolute right-10 bottom-10 h-20 w-28 rounded-[1.6rem] border-2 border-amber-300" />
                      <div className="absolute left-6 bottom-6 rounded-2xl bg-white/90 px-4 py-2 text-xs font-semibold text-slate-900 shadow-lg">
                        Bounding boxes + segmented overlay
                      </div>
                      <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/70 to-transparent" />
                      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-full bg-white/10 px-4 py-1 text-xs text-white backdrop-blur">
                        Frame 87 / 186
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                      <Sparkles className="h-4 w-4 text-emerald-600" /> AI Output
                    </div>
                    <div className="mt-3 space-y-3 text-sm text-slate-600">
                      <div className="flex items-start gap-3 rounded-2xl bg-emerald-50 p-3 ring-1 ring-emerald-100">
                        <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-600" />
                        <div>
                          <div className="font-medium text-slate-900">2 unique polyps detected</div>
                          <div>Tracking IDs 01 and 02 are maintained across frames.</div>
                        </div>
                      </div>
                      <div className="flex items-start gap-3 rounded-2xl bg-sky-50 p-3 ring-1 ring-sky-100">
                        <Waves className="mt-0.5 h-4 w-4 text-sky-600" />
                        <div>
                          <div className="font-medium text-slate-900">Segmented video ready</div>
                          <div>Mask overlays are rendered on top of detected regions.</div>
                        </div>
                      </div>
                      <div className="flex items-start gap-3 rounded-2xl bg-amber-50 p-3 ring-1 ring-amber-100">
                        <Bot className="mt-0.5 h-4 w-4 text-amber-600" />
                        <div>
                          <div className="font-medium text-slate-900">VLM assistant online</div>
                          <div>Ask about size, count, or what can be done now.</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                        <Camera className="h-4 w-4 text-emerald-600" /> Keyframes with unique polyps
                      </div>
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">Sorted by area</span>
                    </div>
                    <div className="mt-4 grid grid-cols-3 gap-3">
                      {keyframes.map((k) => (
                        <button
                          key={k.id}
                          onClick={() => setSelectedKF(k)}
                          className={`rounded-2xl border-2 p-2 text-left transition hover:-translate-y-0.5 ${getColor(k.area)}`}
                        >
                          <div className="aspect-square rounded-xl bg-[radial-gradient(circle_at_30%_30%,rgba(16,185,129,0.18),transparent_42%),linear-gradient(180deg,#ecfdf5,#dbeafe)]" />
                          <div className="mt-2 text-xs font-semibold text-slate-900">{k.id}</div>
                          <div className="text-[11px] text-slate-500">Frame {k.frame}</div>
                          <div className="text-[11px] text-slate-500">Area {k.area}px</div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </Panel>
          </div>

          <div className="space-y-4">
            <Panel title="VLM Assistant" icon={Brain}>
              <div className="rounded-3xl border border-slate-200 bg-gradient-to-b from-emerald-50 to-white p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-slate-900">Polyp-related Q&A</div>
                    <div className="text-xs text-slate-500">Grounded on detection + segmentation summaries</div>
                  </div>
                  <div className="rounded-full bg-white px-3 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-100">Online</div>
                </div>

                <div className="mt-4 h-[360px] space-y-3 overflow-y-auto pr-1">
                  {messages.map((m, idx) => (
                    <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm shadow-sm ${m.role === 'user' ? 'bg-emerald-600 text-white' : 'border border-slate-200 bg-white text-slate-700'}`}>
                        {m.text}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 flex gap-2">
                  <input
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask: What can be done now?"
                    className="flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
                  />
                  <button
                    onClick={handleSend}
                    className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                  >
                    <Send className="h-4 w-4" /> Send
                  </button>
                </div>
              </div>
            </Panel>

            <Panel title="Safety Note" icon={AlertTriangle}>
              <div className="space-y-3 text-sm text-slate-600">
                <div className="flex items-start gap-3 rounded-2xl bg-amber-50 p-3 ring-1 ring-amber-100">
                  <AlertTriangle className="mt-0.5 h-4 w-4 text-amber-600" />
                  <div>
                    <div className="font-medium text-slate-900">AI can make mistakes.</div>
                    <div>Do not rely on the assistant as a final diagnosis tool.</div>
                  </div>
                </div>
                <div className="flex items-start gap-3 rounded-2xl bg-slate-50 p-3">
                  <CircleAlert className="mt-0.5 h-4 w-4 text-slate-500" />
                  <div>
                    <div className="font-medium text-slate-900">Use as decision support only.</div>
                    <div>Clinical follow-up and expert review are still required.</div>
                  </div>
                </div>
              </div>
            </Panel>

            <Panel title="System Snapshot" icon={BadgeInfo}>
              <div className="space-y-3 text-sm text-slate-600">
                <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <span className="font-medium text-slate-700">Detection model</span>
                  <span className="text-slate-900">YOLOv8</span>
                </div>
                <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <span className="font-medium text-slate-700">Segmentation model</span>
                  <span className="text-slate-900">Polyp-PVT</span>
                </div>
                <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <span className="font-medium text-slate-700">Tracking</span>
                  <span className="text-slate-900">Unique polyp IDs</span>
                </div>
                <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <span className="font-medium text-slate-700">Response style</span>
                  <span className="text-slate-900">Medical assistant</span>
                </div>
              </div>
            </Panel>
          </div>
        </div>
      </div>

      {selectedKF && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
          <div className="w-full max-w-md rounded-[2rem] bg-white p-6 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-900">Keyframe Metadata</h3>
              <button onClick={() => setSelectedKF(null)} className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-600">
                Close
              </button>
            </div>
            <div className="space-y-3 text-sm text-slate-700">
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"><span className="text-slate-500">ID</span><span className="font-medium">{selectedKF.id}</span></div>
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"><span className="text-slate-500">Frame number</span><span className="font-medium">{selectedKF.frame}</span></div>
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"><span className="text-slate-500">Area</span><span className="font-medium">{selectedKF.area}px</span></div>
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"><span className="text-slate-500">Confidence</span><span className="font-medium">{selectedKF.confidence}</span></div>
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"><span className="text-slate-500">BBox size</span><span className="font-medium">{selectedKF.bbox}</span></div>
              <div className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3"><span className="text-slate-500">Severity</span><span className="font-medium">{selectedKF.severity}</span></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
