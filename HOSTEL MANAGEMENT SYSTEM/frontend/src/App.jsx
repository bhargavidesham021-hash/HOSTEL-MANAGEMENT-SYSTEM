import React, { useEffect, useMemo, useState } from "react";
import { Link, NavLink, Route, Routes, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Bell,
  BedDouble,
  Building2,
  Check,
  ClipboardList,
  CreditCard,
  DoorOpen,
  Download,
  ArrowLeft,
  Edit,
  Home,
  IndianRupee,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquareWarning,
  Phone,
  Plus,
  Receipt,
  RotateCcw,
  Search,
  ShieldCheck,
  Trash2,
  UserRound,
  Users,
  Utensils,
  WalletCards,
  WashingMachine,
  Wifi,
  X
} from "lucide-react";
import { api, formatMoney, whatsappLink } from "./api";

function currentDateTimeLocal() {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 16);
}

function formatTimestamp(value) {
  return value ? value.replace("T", " ").slice(0, 19) : "-";
}

const adminNav = [
  ["Home", "/admin/home", Home],
  ["Dashboard", "/", LayoutDashboard],
  ["Students", "/students", Users],
  ["Rooms", "/rooms", Building2],
  ["Rent Management", "/payments", CreditCard],
  ["Dues", "/dues", Receipt],
  ["Expenses", "/expenses", WalletCards],
  ["Outings", "/outings", DoorOpen],
  ["Complaints", "/complaints", MessageSquareWarning],
  ["Reports", "/reports", ClipboardList]
];

const studentNav = [
  ["Home", "/student", Home],
  ["Payments", "/student/payments", Receipt],
  ["Outing", "/student/outing", DoorOpen],
  ["Complaints", "/student/complaints", MessageSquareWarning],
  ["Notifications", "/student/notifications", Bell],
  ["Profile", "/student/profile", UserRound]
];

function useFetch(path, fallback) {
  const [data, setData] = useState(fallback);
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true);
    const res = await api.get(path);
    setData(res.data);
    setLoading(false);
  };
  useEffect(() => {
    load().catch(() => setLoading(false));
  }, [path]);
  return { data, loading, reload: load };
}

function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const navigate = useNavigate();
  useEffect(() => {
    api.get("/me").then((res) => setUser(res.data)).catch(() => localStorage.removeItem("jtbh_token")).finally(() => setChecking(false));
  }, []);
  function logout() {
    localStorage.removeItem("jtbh_token");
    setUser(null);
    navigate("/");
  }
  if (checking) return <div className="grid min-h-screen place-items-center">Loading...</div>;
  if (!user) return <PublicSite onLogin={setUser} />;
  if (user.role === "student") return <StudentShell user={user} onLogout={logout} />;
  return <AdminShell user={user} onLogout={logout} />;
}

function PublicSite({ onLogin }) {
  const [login, setLogin] = useState(null);
  if (login) return <LoginPanel mode={login} onBack={() => setLogin(null)} onLogin={onLogin} />;
  const facilities = [
    ["Free Wi-Fi", "Stay connected for studies and entertainment.", Wifi],
    ["Homely Food", "Daily food prepared for hostel residents.", Utensils],
    ["CCTV Security", "Security monitoring for residents.", ShieldCheck],
    ["Hot Water", "Hot water facility available.", Check],
    ["Washing Machine", "Convenient clothes washing facility.", WashingMachine],
    ["Drinking Water", "Clean drinking water for students.", Check]
  ];
  return (
    <div className="bg-white text-ink">
      <header className="sticky top-0 z-30 border-b border-slate-100 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <a href="#home" className="font-bold text-brand">JAI TULJA BHAVANI</a>
          <nav className="hidden items-center gap-6 text-sm font-semibold md:flex">
            {["Home", "About", "Facilities", "Rooms", "Contact"].map((item) => <a key={item} href={`#${item.toLowerCase()}`} className="hover:text-brand">{item}</a>)}
          </nav>
          <div className="flex gap-2">
            <button className="btn-muted" onClick={() => setLogin("student")}>Student Login</button>
            <button className="btn-primary" onClick={() => setLogin("admin")}>Admin Login</button>
          </div>
        </div>
      </header>
      <section id="home" className="relative overflow-hidden bg-slate-950 text-white">
        <div className="absolute inset-0 bg-[linear-gradient(120deg,rgba(15,118,110,.92),rgba(15,23,42,.82)),url('https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=1600&q=80')] bg-cover bg-center" />
        <div className="relative mx-auto grid min-h-[88vh] max-w-7xl content-center gap-8 px-4 py-20 md:grid-cols-[1fr_.8fr]">
          <motion.div initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
            <p className="text-sm font-semibold uppercase tracking-widest text-teal-100">Near Aurora College, Aushapur</p>
            <h1 className="mt-4 max-w-3xl text-4xl font-black leading-tight md:text-6xl">JAI TULJA BHAVANI DELUXE BOYS HOSTEL</h1>
            <p className="mt-5 max-w-2xl text-lg text-teal-50">A comfortable home away from home. Safe, hygienic, comfortable, and student friendly.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <a className="btn-primary bg-white text-brand hover:bg-teal-50" href="#contact">Enquire Now</a>
              <a className="btn-muted bg-white/15 text-white hover:bg-white/25" href="tel:9822222064"><Phone size={16} /> Call Now</a>
              <button className="btn-muted bg-white/15 text-white hover:bg-white/25" onClick={() => setLogin("student")}>Student Login</button>
              <button className="btn-muted bg-white/15 text-white hover:bg-white/25" onClick={() => setLogin("admin")}>Admin Login</button>
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, y: 36 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.1 }} className="rounded-lg border border-white/15 bg-white/10 p-5 backdrop-blur-sm">
            <div className="grid grid-cols-2 gap-3">{[["3", "Floors"], ["10", "Rooms"], ["70", "Capacity"], ["7", "Students per room"]].map(([n, l]) => <div key={l} className="rounded-lg bg-white p-5 text-ink"><p className="text-3xl font-black text-brand">{n}</p><p className="text-sm font-semibold">{l}</p></div>)}</div>
          </motion.div>
        </div>
      </section>
      <Section id="about" title="About Hostel"><p className="max-w-3xl text-slate-600">Jai Tulja Bhavani Deluxe Boys Hostel provides a comfortable and student-friendly living environment near Aurora College, Aushapur. Our hostel combines essential facilities, security and a homely atmosphere to help students stay comfortable while focusing on their education.</p></Section>
      <Section id="details" title="Hostel Details"><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"><InfoCard title="Hostel Name" value="Jai Tulja Bhavani Deluxe Boys Hostel" /><InfoCard title="Address / Location" value="Near Aurora College, Aushapur" /><InfoCard title="Total Capacity" value="70 students across 10 rooms" /><InfoCard title="Contact Information" value="9822222064" /><InfoCard title="Rules & Policies" value="Maintain cleanliness, respect quiet hours, and follow hostel safety guidelines." /><InfoCard title="Facilities" value="Washing machine, hot water, free Wi-Fi, CCTV security, food, and drinking water." /></div></Section>
      <Section id="facilities" title="Why Choose Our Hostel?"><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{facilities.map(([title, text, Icon], index) => <motion.div key={title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: index * 0.04 }} className="card p-5"><Icon className="text-brand" /><h3 className="mt-4 font-bold">{title}</h3><p className="mt-2 text-sm text-slate-600">{text}</p></motion.div>)}</div></Section>
      <Section id="rooms" title="Room Information"><div className="grid gap-4 md:grid-cols-3"><InfoCard title="Floor 1" value="4 Rooms - 28 Students" /><InfoCard title="Floor 2" value="4 Rooms - 28 Students" /><InfoCard title="Floor 3" value="2 Rooms - 14 Students" /></div><div className="mt-5 grid gap-4 md:grid-cols-2"><InfoCard title="Bedroom" value="4 students per room" /><InfoCard title="Hall" value="3 students per room" /></div></Section>
      <Section id="contact" title="Contact"><div className="card p-5"><h3 className="font-bold">Jai Tulja Bhavani Deluxe Boys Hostel</h3><p className="mt-2 text-slate-600">Near Aurora College, Aushapur</p><p className="mt-1 font-semibold">9822222064</p><div className="mt-4 flex flex-wrap gap-2"><a className="btn-primary" href="tel:9822222064">Call Hostel</a><a className="btn-muted" href={`https://wa.me/919822222064?text=${encodeURIComponent("Hello, I would like to know about room availability at Jai Tulja Bhavani Deluxe Boys Hostel.")}`} target="_blank">WhatsApp</a><a className="btn-muted" href="https://www.google.com/maps/search/?api=1&query=Near+Aurora+College+Aushapur" target="_blank">Get Directions</a></div></div></Section>
      <footer className="bg-slate-950 px-4 py-8 text-white"><div className="mx-auto max-w-7xl"><b>JAI TULJA BHAVANI DELUXE BOYS HOSTEL</b><p className="mt-2 text-sm text-slate-300">Near Aurora College, Aushapur - 9822222064</p><p className="mt-5 text-xs text-slate-400">2026 Jai Tulja Bhavani Deluxe Boys Hostel. All Rights Reserved.</p></div></footer>
    </div>
  );
}

function Section({ id, title, children }) {
  return <section id={id} className="mx-auto max-w-7xl px-4 py-16"><motion.h2 initial={{ opacity: 0, y: 18 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="mb-6 text-3xl font-black">{title}</motion.h2>{children}</section>;
}

function InfoCard({ title, value }) {
  return <div className="card p-5"><h3 className="font-bold">{title}</h3><p className="mt-2 text-slate-600">{value}</p></div>;
}

function LoginPanel({ mode, onBack, onLogin }) {
  const [creatingAccount, setCreatingAccount] = useState(false);
  const [form, setForm] = useState(mode === "admin" ? { name: "", email: "", password: "", confirmPassword: "" } : { identifier: "", password: "" });
  const [error, setError] = useState("");
  const isAdmin = mode === "admin";
  function switchAdminView() {
    setCreatingAccount((value) => !value);
    setError("");
    setForm({ name: "", email: "", password: "", confirmPassword: "" });
  }
  async function submit(e) {
    e.preventDefault();
    setError("");
    if (creatingAccount && form.password !== form.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    try {
      const path = isAdmin ? (creatingAccount ? "/auth/register" : "/auth/login") : "/auth/student-login";
      const payload = isAdmin ? (creatingAccount ? { name: form.name, email: form.email, password: form.password } : { email: form.email, password: form.password }) : { identifier: form.identifier, password: form.password };
      const res = await api.post(path, payload);
      localStorage.setItem("jtbh_token", res.data.access_token);
      onLogin(res.data.user);
    } catch (requestError) {
      setError(requestError.response?.data?.error || "Invalid login details");
    }
  }
  return <div className="grid min-h-screen place-items-center bg-surface p-4"><form onSubmit={submit} className="card w-full max-w-md p-5 sm:p-6"><button type="button" className="text-sm font-semibold text-brand" onClick={onBack}>Back to website</button><h1 className="mt-4 text-2xl font-bold">{isAdmin ? (creatingAccount ? "Create Admin Account" : "Admin Login") : "Student Login"}</h1><p className="mt-1 text-sm text-slate-500">Jai Tulja Bhavani Deluxe Boys Hostel</p><div className="mt-6 space-y-3">{creatingAccount && <input required autoComplete="name" className="input" placeholder="Full name" value={form.name || ""} onChange={(e) => setForm({ ...form, name: e.target.value })} />}{isAdmin ? <input required autoComplete="username" className="input" placeholder="Email or username" value={form.email || ""} onChange={(e) => setForm({ ...form, email: e.target.value })} /> : <input required className="input" placeholder="Student ID or phone" value={form.identifier || ""} onChange={(e) => setForm({ ...form, identifier: e.target.value })} />}<input required minLength={creatingAccount ? 8 : undefined} autoComplete={creatingAccount ? "new-password" : "current-password"} className="input" type="password" placeholder={creatingAccount ? "Password (minimum 8 characters)" : "Password"} value={form.password || ""} onChange={(e) => setForm({ ...form, password: e.target.value })} />{creatingAccount && <input required autoComplete="new-password" className="input" type="password" placeholder="Confirm password" value={form.confirmPassword || ""} onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })} />}{error && <p role="alert" className="text-sm text-red-600">{error}</p>}<button className="btn-primary w-full">{creatingAccount ? "Create Account" : "Login"}</button>{isAdmin && <button type="button" className="w-full text-sm font-semibold text-brand hover:underline" onClick={switchAdminView}>{creatingAccount ? "Already have an account? Log in" : "Create an admin account"}</button>}</div></form></div>;
}

function AdminShell({ user, onLogout }) {
  const [open, setOpen] = useState(false);
  return <div className="min-h-screen bg-surface md:flex"><aside className={`fixed inset-y-0 left-0 z-40 w-72 bg-white border-r border-slate-200 transition md:static md:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}><div className="flex h-16 items-center justify-between border-b border-slate-100 px-5"><div><p className="text-sm font-bold text-brand">JTBH</p><p className="text-xs text-slate-500">Admin Panel</p></div><button className="md:hidden" onClick={() => setOpen(false)}><X size={20} /></button></div><nav className="space-y-1 p-3">{adminNav.map(([label, to, Icon]) => <NavItem key={to} label={label} to={to} icon={Icon} close={() => setOpen(false)} />)}</nav></aside><div className="flex min-w-0 flex-1 flex-col"><Topbar user={user} onLogout={onLogout} openMenu={() => setOpen(true)} /><main className="p-4 md:p-6"><AdminRoutes /></main></div><DashboardModalHost /><RoomAssignmentHost /></div>;
}

function StudentShell({ onLogout }) {
  return <div className="min-h-screen bg-surface pb-20 md:pb-0"><header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4"><b className="text-brand">JTBH Student</b><button className="btn-muted" onClick={onLogout}><LogOut size={18} /></button></header><main className="p-4 md:p-6"><StudentRoutes /></main><nav className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-6 border-t border-slate-200 bg-white md:hidden">{studentNav.map(([label, to, Icon]) => <NavLink key={to} to={to} className={({ isActive }) => `grid place-items-center gap-1 py-2 text-[10px] font-semibold ${isActive ? "text-brand" : "text-slate-500"}`}><Icon size={18} />{label}</NavLink>)}</nav></div>;
}

function Topbar({ user, onLogout, openMenu }) {
  return <header className="sticky top-0 z-30 flex h-16 min-w-0 items-center gap-3 border-b border-slate-200 bg-white px-4"><button className="btn-muted md:hidden" onClick={openMenu}><Menu size={18} /></button><div className="relative min-w-0 max-w-xl flex-1"><Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} /><input className="input min-w-0 pl-10" placeholder="Search student, phone, room, college" /></div><button className="btn-muted shrink-0"><Bell size={18} /></button><div className="hidden text-right sm:block"><p className="text-sm font-semibold">{user?.name}</p><p className="text-xs capitalize text-slate-500">{user?.role}</p></div><button className="btn-muted shrink-0" onClick={onLogout}><LogOut size={18} /></button></header>;
}

function NavItem({ label, to, icon: Icon, close }) {
  return <NavLink to={to} onClick={close} className={({ isActive }) => `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-semibold ${isActive ? "bg-teal-50 text-brand" : "text-slate-600 hover:bg-slate-50"}`}><Icon size={18} /> {label}</NavLink>;
}

function AdminRoutes() {
  return <Routes><Route path="/" element={<Dashboard />} /><Route path="/admin/home" element={<AdminHome />} /><Route path="/students" element={<Students />} /><Route path="/students/:id" element={<StudentProfile />} /><Route path="/rooms" element={<Rooms />} /><Route path="/rooms/:id" element={<RoomDetail />} /><Route path="/payments" element={<Payments />} /><Route path="/dues" element={<Dues />} /><Route path="/expenses" element={<Expenses />} /><Route path="/outings" element={<Outings />} /><Route path="/complaints" element={<Complaints />} /><Route path="/reports" element={<Reports />} /></Routes>;
}

function StudentRoutes() {
  return <Routes><Route path="/student" element={<StudentHome />} /><Route path="/student/payments" element={<StudentPayments />} /><Route path="/student/outing" element={<StudentOuting />} /><Route path="/student/complaints" element={<StudentComplaints />} /><Route path="/student/notifications" element={<StudentNotifications />} /><Route path="/student/profile" element={<StudentProfileSelf />} /><Route path="*" element={<StudentHome />} /></Routes>;
}

function Page({ title, action, children }) {
  const navigate = useNavigate();
  return <><div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between"><h1 className="text-2xl font-bold">{title}</h1>{action}</div>{children}<footer className="mt-8 flex justify-start border-t border-slate-200 pt-4"><button className="btn-muted" onClick={() => navigate(-1)} aria-label="Back"><ArrowLeft size={16} /> Back</button></footer></>;
}

function Stat({ label, value, icon: Icon }) {
  const interactive = ["Current Students", "Available Slots", "This Month Collected", "This Month Pending"].includes(label);
  function openDetails() {
    if (interactive) window.dispatchEvent(new CustomEvent("dashboard-metric", { detail: label }));
  }
  return <div className={`card p-4 ${interactive ? "cursor-pointer transition hover:bg-teal-50 hover:shadow-md" : ""}`} onClick={openDetails} role={interactive ? "button" : undefined} tabIndex={interactive ? 0 : undefined} onKeyDown={(event) => interactive && event.key === "Enter" && openDetails()}><div className="flex items-center justify-between"><p className="text-sm text-slate-500">{label}</p><Icon className="text-brand" size={20} /></div><p className="mt-2 text-2xl font-bold">{value ?? 0}</p></div>;
}

function AdminHome() {
  const { data } = useFetch("/dashboard", { summary: {}, rooms: [], outing_summary: {} });
  const summary = data.summary;
  const occupancyRate = summary.total_capacity ? Math.round((summary.occupied_slots / summary.total_capacity) * 100) : 0;
  return <Page title="Home"><section className="mb-5 rounded-lg bg-brand p-6 text-white"><p className="text-sm font-semibold uppercase tracking-widest text-teal-100">Jai Tulja Bhavani Deluxe Boys Hostel</p><h2 className="mt-2 text-3xl font-black">Hostel Details</h2><p className="mt-2 text-teal-50">A comfortable, secure, and student-friendly home near Aurora College, Aushapur.</p></section><section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"><InfoCard title="Hostel Name" value="Jai Tulja Bhavani Deluxe Boys Hostel" /><InfoCard title="Address / Location" value="Near Aurora College, Aushapur" /><InfoCard title="Contact Info" value="9822222064" /><InfoCard title="Emergency Contact" value="Hostel Office: 9822222064" /></section><section className="mt-5"><h2 className="mb-3 text-xl font-bold">Overview Stats</h2><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Stat label="Total Rooms" value={data.rooms.length} icon={Building2} /><Stat label="Total Bed Capacity" value={summary.total_capacity} icon={BedDouble} /><Stat label="Current Occupants" value={summary.occupied_slots} icon={Users} /><Stat label="Occupancy Rate" value={`${occupancyRate}%`} icon={Building2} /></div></section><section className="mt-5 grid gap-5 lg:grid-cols-2"><div className="card p-5"><h2 className="font-bold">Rules & Policies</h2><ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-600"><li>Maintain cleanliness in rooms and shared areas.</li><li>Respect quiet hours and fellow residents.</li><li>Follow visitor, outing, and hostel safety procedures.</li></ul></div><div className="card p-5"><h2 className="font-bold">Facilities & Notices</h2><p className="mt-3 text-sm text-slate-600">Free Wi-Fi, hot water, washing machine, CCTV security, homely food, and drinking water are available.</p></div></section></Page>;
}

function DataList({ headers, children, className = "" }) {
  const rows = React.Children.map(children, (row) => {
    if (!React.isValidElement(row)) return row;
    let column = 0;
    const labelCells = (cell) => {
      if (!React.isValidElement(cell)) return cell;
      if (cell.type === "td") return React.cloneElement(cell, { "data-label": headers[column++] || "" });
      if (cell.type === React.Fragment) return React.cloneElement(cell, {}, React.Children.map(cell.props.children, labelCells));
      return cell;
    };
    const cells = React.Children.map(row.props.children, labelCells);
    return React.cloneElement(row, {}, cells);
  });
  return <div className={`card overflow-hidden ${className}`}><table className="w-full border-collapse text-left text-sm"><thead className="hidden bg-slate-50 text-xs uppercase text-slate-500 md:table-header-group"><tr>{headers.map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr></thead><tbody className="block divide-y divide-slate-100 p-4 md:table-row-group md:p-0 [&_td]:block [&_td]:py-1 md:[&_td]:table-cell md:[&_td]:px-4 md:[&_td]:py-3">{rows}</tbody></table></div>;
}

function DashboardModal({ title, onClose, search, setSearch, children }) {
  return <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4" role="dialog" aria-modal="true"><section className="max-h-[90vh] w-full max-w-4xl overflow-hidden rounded-lg bg-white shadow-xl"><header className="flex items-center justify-between border-b border-slate-200 px-5 py-4"><h2 className="text-xl font-bold">{title}</h2><button className="btn-muted" onClick={onClose} aria-label="Close"><X size={18} /></button></header><div className="border-b border-slate-100 p-4"><input autoFocus className="input" placeholder="Search by name, phone, room, or bed" value={search} onChange={(e) => setSearch(e.target.value)} /></div><div className="max-h-[65vh] overflow-y-auto p-4">{children}</div></section></div>;
}

function ConfirmDialog({ title, message, onCancel, onConfirm }) {
  return <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4" role="dialog" aria-modal="true"><section className="w-full max-w-md rounded-lg bg-white p-5 shadow-xl"><h2 className="text-xl font-bold">{title}</h2><p className="mt-3 text-sm text-slate-600">{message}</p><div className="mt-5 flex justify-end gap-2"><button className="btn-muted" onClick={onCancel}>Cancel</button><button className="btn-primary bg-red-700 hover:bg-red-800" onClick={onConfirm}>Delete</button></div></section></div>;
}

function DashboardModalHost() {
  const [modal, setModal] = useState(null);
  const [search, setSearch] = useState("");
  const { data: students } = useFetch("/students?status=Active", { students: [] });
  const { data: slots } = useFetch("/available-slots", { slots: [] });
  const { data: dashboardData } = useFetch(`/dashboard?month=${new Date().toISOString().slice(0, 7)}`, { summary: {} });
  useEffect(() => {
    const open = (event) => { setModal(event.detail); setSearch(""); };
    window.addEventListener("dashboard-metric", open);
    return () => window.removeEventListener("dashboard-metric", open);
  }, []);
  if (!modal) return null;
  const query = search.toLowerCase();
  if (modal === "This Month Collected") {
    const collected = dashboardData.summary?.collected_details || [];
    return <DashboardModal title="This Month Collected" onClose={() => setModal(null)} search={search} setSearch={setSearch}>{collected.length ? <DataList headers={["Payer", "Room", "Method", "Transaction Date & Time", "Amount"]}>{collected.filter((payment) => [payment.payer, payment.room, payment.method, payment.timestamp].some((value) => String(value).toLowerCase().includes(query))).map((payment) => <tr key={payment.id} className="mobile-row"><td>{payment.payer}</td><td>Room {payment.room || "-"}</td><td>{payment.method}</td><td>{payment.timestamp}</td><td>{formatMoney(payment.amount)}</td></tr>)}</DataList> : <p className="py-8 text-center text-slate-500">No successful payments recorded this month.</p>}</DashboardModal>;
  }
  if (modal === "This Month Pending") {
    const overdue = dashboardData.summary?.overdue_details || [];
    const filtered = overdue.filter((item) => [item.student, item.phone, item.room, item.due_date].some((value) => String(value).toLowerCase().includes(query)));
    return <DashboardModal title={`This Month Pending (${overdue.length} overdue)`} onClose={() => setModal(null)} search={search} setSearch={setSearch}>{filtered.length ? <DataList headers={["Student", "Room", "Due Date", "Unpaid Balance", "Action"]}>{filtered.map((item) => <tr key={item.id} className="mobile-row"><td>{item.student}<br /><span className="text-xs text-slate-500">{item.phone}</span></td><td>Room {item.room || "-"}</td><td>{item.due_date}</td><td>{formatMoney(item.balance)}</td><td><a className="btn-muted" target="_blank" href={whatsappLink({ full_name: item.student, phone: item.phone }, item.balance, item.due_date)}>Send Reminder</a></td></tr>)}</DataList> : <p className="py-8 text-center text-slate-500">No overdue balances found.</p>}</DashboardModal>;
  }
  if (modal === "Current Students") {
    const occupied = students.students.filter((student) => student.room && student.slot && [student.full_name, student.phone, student.room, student.slot].some((value) => String(value).toLowerCase().includes(query)));
    return <DashboardModal title="Current Students" onClose={() => setModal(null)} search={search} setSearch={setSearch}>{occupied.length ? <DataList headers={["Full Name", "Phone", "Room & Bed", "Joining Date/Time", "Payment Status"]}>{occupied.map((student) => <tr key={student.id} className="mobile-row"><td>{student.full_name}</td><td>{student.phone}</td><td>Room {student.room} - {student.area} {student.slot}</td><td>{formatTimestamp(student.joining_date)}</td><td><StatusBadge status={student.payment_status} /><br />{formatMoney(student.balance)} due</td></tr>)}</DataList> : <p className="py-8 text-center text-slate-500">No occupied students found.</p>}</DashboardModal>;
  }
  const available = slots.slots.filter((slot) => [slot.room, slot.area, slot.code].some((value) => String(value).toLowerCase().includes(query)));
  const grouped = available.reduce((groups, slot) => { const key = String(slot.room); (groups[key] ||= []).push(slot); return groups; }, {});
  return <DashboardModal title="Available Slots" onClose={() => setModal(null)} search={search} setSearch={setSearch}>{available.length ? <div className="space-y-5">{Object.entries(grouped).map(([room, roomSlots]) => <section key={room}><h3 className="mb-2 font-bold">Room {room}</h3><div className="grid gap-2 sm:grid-cols-2">{roomSlots.map((slot) => <div key={slot.id} className="flex items-center justify-between rounded-md border border-slate-200 p-3"><span><b>{slot.area}</b><br /><span className="text-sm text-slate-500">Vacant bed {slot.code}</span></span><Link className="btn-primary" to={`/students?slot_id=${slot.id}`} onClick={() => setModal(null)}><Plus size={16} /> Assign / Add Student</Link></div>)}</div></section>)}</div> : <p className="py-8 text-center text-slate-500">No available slots found.</p>}</DashboardModal>;
}

function RoomAssignmentHost() {
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [search, setSearch] = useState("");
  const [slotId, setSlotId] = useState("");
  const { data: slots, reload: reloadSlots } = useFetch("/available-slots", { slots: [] });
  const { data: students, reload: reloadStudents } = useFetch("/students?status=Active", { students: [] });
  useEffect(() => {
    const open = (event) => { setRoom(event.detail); setSearch(""); setSlotId(""); };
    window.addEventListener("room-assignment", open);
    return () => window.removeEventListener("room-assignment", open);
  }, []);
  if (!room) return null;
  const roomSlots = slots.slots.filter((slot) => String(slot.room) === String(room.number));
  const selectedSlot = roomSlots.find((slot) => String(slot.id) === String(slotId)) || roomSlots[0];
  const query = search.toLowerCase();
  const candidates = students.students.filter((student) => [student.full_name, student.phone, student.room, student.slot].some((value) => String(value || "").toLowerCase().includes(query)));
  async function assignExisting(student) {
    if (!selectedSlot) return;
    await api.post(`/students/${student.id}/transfer`, { slot_id: selectedSlot.id });
    reloadSlots();
    reloadStudents();
  }
  return <DashboardModal title={`Assign Student to Room ${room.number}`} onClose={() => setRoom(null)} search={search} setSearch={setSearch}><div className="mb-5 flex flex-wrap items-end gap-3"><label className="text-sm font-semibold">Vacant bed<select className="input mt-1 w-52" value={selectedSlot?.id || ""} onChange={(event) => setSlotId(event.target.value)}>{roomSlots.length ? roomSlots.map((slot) => <option key={slot.id} value={slot.id}>{slot.area} {slot.code}</option>) : <option>No vacant beds</option>}</select></label><button className="btn-primary" disabled={!selectedSlot} onClick={() => navigate(`/students?slot_id=${selectedSlot.id}`)}><Plus size={16} /> Add New Student</button></div><h3 className="mb-2 font-bold">Assign Existing Student</h3>{candidates.length ? <DataList headers={["Student", "Phone", "Current Room", "Bed", "Action"]}>{candidates.map((student) => <tr key={student.id} className="mobile-row"><td>{student.full_name}</td><td>{student.phone}</td><td>{student.room ? `Room ${student.room}` : "Unassigned"}</td><td>{student.area ? `${student.area} ${student.slot}` : "-"}</td><td><button className="btn-muted" disabled={!selectedSlot || String(student.room) === String(room.number)} onClick={() => assignExisting(student)}>Assign to {selectedSlot?.code || "bed"}</button></td></tr>)}</DataList> : <p className="py-6 text-center text-slate-500">No matching students found.</p>}</DashboardModal>;
}

function Dashboard() {
  const { data } = useFetch("/dashboard", { summary: {}, rooms: [], outing_summary: {} });
  const s = data.summary;
  return <Page title="Dashboard"><div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><Stat label="Total Capacity" value={s.total_capacity} icon={BedDouble} /><Stat label="Current Students" value={s.current_students} icon={Users} /><Stat label="Available Slots" value={s.available_slots} icon={Building2} /><Stat label="This Month Expected" value={formatMoney(s.monthly_expected_income)} icon={IndianRupee} /><Stat label="This Month Collected" value={formatMoney(s.monthly_collected_amount)} icon={CreditCard} /><Stat label="This Month Pending" value={formatMoney(s.pending_amount)} icon={Receipt} /><Stat label="Total Expenses" value={formatMoney(s.total_expenses)} icon={WalletCards} /><Stat label="Net Income" value={formatMoney(s.net_income)} icon={IndianRupee} /></div><section className="card mt-5 p-4"><div className="flex items-center justify-between"><h2 className="font-bold">Outings Today</h2><Link className="btn-muted" to="/outings">View Outings</Link></div><div className="mt-3 grid grid-cols-2 gap-3"><Stat label="Requests" value={data.outing_summary.total} icon={DoorOpen} /><Stat label="Currently Out" value={data.outing_summary.currently_out} icon={DoorOpen} /><Stat label="Returned" value={data.outing_summary.returned} icon={Check} /><Stat label="Late" value={data.outing_summary.late} icon={Bell} /></div></section><section className="card mt-5 p-4"><div className="flex items-center justify-between"><h2 className="font-bold">Room Occupancy</h2><Link className="btn-muted" to="/rooms"><Edit size={16} /> Room Extension</Link></div><div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-4">{data.rooms.map((room) => <RoomMini key={room.id} room={room} />)}</div></section></Page>;
}

function RoomMini({ room }) {
  const tone = !room.is_active ? "bg-slate-300" : room.available === 0 ? "bg-red-500" : room.available <= 1 ? "bg-orange-500" : "bg-emerald-500";
  return <div className="rounded-md border border-slate-100 bg-white p-3 hover:bg-slate-50"><Link to={`/rooms/${room.id}`} className="block"><div className="flex items-center justify-between"><b>Room {room.number}</b><span className="text-sm">{room.occupied}/{room.capacity}</span></div><div className="mt-2 grid grid-cols-7 gap-1">{Array.from({ length: room.capacity || 7 }).map((_, i) => <span key={i} className={`h-2 rounded ${i < room.occupied ? tone : "bg-slate-200"}`} />)}</div><p className="mt-2 text-xs text-slate-500">Bedroom {room.bedroom_occupied}/{room.bedroom_capacity} - Hall {room.hall_occupied}/{room.hall_capacity}</p></Link><div className="mt-3 grid grid-cols-2 gap-2"><button className="btn-primary" onClick={() => window.dispatchEvent(new CustomEvent("room-assignment", { detail: room }))}><Plus size={16} /> Add Student</button><Link className="btn-muted" to="/rooms"><Edit size={16} /> Bed Extension</Link></div></div>;
}

function Students() {
  const [status, setStatus] = useState("Active");
  const [sort, setSort] = useState("newest");
  const [searchParams] = useSearchParams();
  const { data, reload } = useFetch(`/students?status=${status}`, { students: [] });
  const { data: slotsData, reload: reloadSlots } = useFetch("/available-slots", { slots: [] });
  const [form, setForm] = useState({ slot_id: searchParams.get("slot_id") || "" });
  async function submit(e) {
    e.preventDefault();
    await api.post("/students", form);
    setForm({});
    reload();
    reloadSlots();
  }
  async function removeStudent(student) {
    if (!window.confirm(`Are you sure you want to remove this student?\n\nStudent: ${student.full_name}\nID: ${student.student_code}\nRoom: ${student.room || "Unallocated"}\nPending: ${formatMoney(student.balance)}`)) return;
    await api.post(`/students/${student.id}/remove`, { reason: "Removed by admin" });
    reload();
    reloadSlots();
  }
  async function restoreStudent(student) {
    await api.post(`/students/${student.id}/restore`);
    reload();
  }
  async function transferStudent(student) {
    const slotId = window.prompt("Enter available slot ID from the room allocation dropdown:");
    if (!slotId) return;
    await api.post(`/students/${student.id}/transfer`, { slot_id: slotId });
    reload();
    reloadSlots();
  }
  const sortedStudents = [...data.students].sort((a, b) => sort === "newest" ? (b.created_at || "").localeCompare(a.created_at || "") : (a.created_at || "").localeCompare(b.created_at || ""));
  return <Page title="Students"><section className="card p-4"><div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between"><h2 className="font-bold">Add Student</h2><div className="flex gap-2"><select className="input w-full md:w-52" value={status} onChange={(e) => setStatus(e.target.value)}>{["Active", "Checked Out", "Removed", "All"].map((s) => <option key={s}>{s}</option>)}</select><select className="input w-36" value={sort} onChange={(e) => setSort(e.target.value)}><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></div></div><form onSubmit={submit} className="mt-3 grid gap-3 md:grid-cols-3"><input required className="input" placeholder="Full name" value={form.full_name || ""} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /><input required className="input" placeholder="Phone" value={form.phone || ""} onChange={(e) => setForm({ ...form, phone: e.target.value })} /><input className="input" type="datetime-local" value={form.joining_date || currentDateTimeLocal()} onChange={(e) => setForm({ ...form, joining_date: e.target.value })} /><input className="input" placeholder="College" value={form.college_name || ""} onChange={(e) => setForm({ ...form, college_name: e.target.value })} /><input className="input" placeholder="Course" value={form.course || ""} onChange={(e) => setForm({ ...form, course: e.target.value })} /><input className="input" type="number" placeholder="Monthly rent" value={form.monthly_rent || ""} onChange={(e) => setForm({ ...form, monthly_rent: e.target.value })} /><input className="input" type="password" placeholder="Student portal password" value={form.password || ""} onChange={(e) => setForm({ ...form, password: e.target.value })} /><select className="input" value={form.slot_id || ""} onChange={(e) => setForm({ ...form, slot_id: e.target.value })}><option value="">No slot yet</option>{slotsData.slots.map((s) => <option key={s.id} value={s.id}>ID {s.id} - Floor {s.floor} - Room {s.room} - {s.area} {s.code}</option>)}</select><input className="input" placeholder="Guardian name" value={form.guardian_name || ""} onChange={(e) => setForm({ ...form, guardian_name: e.target.value })} /><input className="input" placeholder="Guardian phone" value={form.guardian_phone || ""} onChange={(e) => setForm({ ...form, guardian_phone: e.target.value })} /><button className="btn-primary"><Plus size={16} /> Save Student</button></form></section><DataList className="mt-5" headers={["Student", "Joined", "Phone", "Room", "Slot", "Rent", "Payment", "Status", "Actions"]}>{sortedStudents.map((s) => <tr key={s.id} className="mobile-row"><td><Link className="font-semibold text-brand" to={`/students/${s.id}`}>{s.full_name}<br /><span className="text-xs text-slate-500">{s.student_code}</span></Link></td><td>{formatTimestamp(s.joining_date)}</td><td>{s.phone}</td><td>{s.room || "Unallocated"}</td><td>{s.area} {s.slot}</td><td>{formatMoney(s.monthly_rent)}</td><td><StatusBadge status={s.payment_status} /></td><td>{s.status}</td><td><div className="flex flex-wrap gap-2"><Link className="btn-muted" to={`/students/${s.id}`}>View</Link><Link className="btn-muted" to="/payments">Payment</Link><button className="btn-muted" onClick={() => transferStudent(s)}>Move</button><button className="btn-muted" onClick={() => api.post(`/students/${s.id}/checkout`).then(reload)}>Checkout</button><a className="btn-muted" href={whatsappLink(s, s.balance, "current month")} target="_blank">WhatsApp</a>{s.status === "Removed" ? <button className="btn-muted" onClick={() => restoreStudent(s)}><RotateCcw size={14} /> Restore</button> : <button className="btn-muted text-red-700" onClick={() => removeStudent(s)}><Trash2 size={14} /> Remove</button>}</div></td></tr>)}</DataList></Page>;
}

function BedControl({ room, reload }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function change(delta) {
    setBusy(true); setError("");
    try {
      const { data } = await api.get(`/rooms/${room.id}`);
      const vacant = data.slots.find(slot => !slot.is_occupied);
      if (delta < 0 && !vacant) throw new Error("Cannot reduce capacity below occupied beds or zero");
      const key = delta > 0 || vacant.area === "Bedroom" ? "bedroom_capacity" : "hall_capacity";
      await api.put(`/rooms/${room.id}`, { [key]: data[key] + delta });
      await reload(); setOpen(false);
    } catch (e) { setError(e.response?.data?.error || e.message); }
    finally { setBusy(false); }
  }
  return <div className="mt-3"><button className="btn-muted" aria-label={`Manage beds for Room ${room.number}`} aria-expanded={open} onClick={() => setOpen(!open)}>+/-</button>{open && <div className="mt-2 flex gap-2"><button disabled={busy} className="btn-muted" onClick={() => change(1)}>+ Add Bed</button><button disabled={busy || room.capacity === 0 || room.occupied >= room.capacity} className="btn-muted" onClick={() => change(-1)}>- Delete Bed</button></div>}{error && <p role="alert" className="text-sm text-red-700">{error}</p>}</div>;
}

function Rooms() {
  const { data, reload } = useFetch("/rooms", { floors: [] });
  const [showEditor, setShowEditor] = useState(false);
  const [roomId, setRoomId] = useState("");
  const [form, setForm] = useState({ bedroom_capacity: 4, hall_capacity: 3 });
  const [newRoom, setNewRoom] = useState({ floor: 1, number: "", bedroom_capacity: 4, hall_capacity: 3 });
  const rooms = data.floors.flatMap((floor) => floor.rooms);
  function selectRoom(value) {
    const room = rooms.find((item) => String(item.id) === String(value));
    setRoomId(value);
    if (room) setForm({ bedroom_capacity: room.bedroom_capacity, hall_capacity: room.hall_capacity });
  }
  async function updateCapacity(event) {
    event.preventDefault();
    await api.put(`/rooms/${roomId}`, form);
    await reload();
    setShowEditor(false);
  }
  async function addRoom(event) {
    event.preventDefault();
    await api.post("/rooms", newRoom);
    await reload();
    setNewRoom({ floor: 1, number: "", bedroom_capacity: 4, hall_capacity: 3 });
  }
  return <Page title="Hostel Layout" action={<button className="btn-primary" onClick={() => { setShowEditor(true); if (!roomId && rooms[0]) selectRoom(rooms[0].id); }}><Edit size={16} /> Expand Capacity / Edit Rooms</button>}>{data.floors.map((floor) => <section key={floor.id} className="mb-5"><h2 className="mb-3 font-bold">Floor {floor.number}</h2><div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">{floor.rooms.map((room) => <div key={room.id} className="card p-4"><RoomMini room={room} /><BedControl room={room} reload={reload} /></div>)}</div></section>)}{showEditor && <DashboardModal title="Expand Capacity / Edit Rooms" onClose={() => setShowEditor(false)} search="" setSearch={() => {}}><form onSubmit={updateCapacity} className="grid gap-3 md:grid-cols-3"><label className="text-sm font-semibold">Room<select className="input mt-1" value={roomId} onChange={(event) => selectRoom(event.target.value)}>{rooms.map((room) => <option key={room.id} value={room.id}>Room {room.number}</option>)}</select></label><label className="text-sm font-semibold">Bedroom beds<input required className="input mt-1" type="number" min="0" value={form.bedroom_capacity} onChange={(event) => setForm({ ...form, bedroom_capacity: event.target.value })} /></label><label className="text-sm font-semibold">Hall beds<input required className="input mt-1" type="number" min="0" value={form.hall_capacity} onChange={(event) => setForm({ ...form, hall_capacity: event.target.value })} /></label><button className="btn-primary">Save Room Capacity</button></form><hr className="my-6" /><h3 className="mb-3 font-bold">Add New Room</h3><form onSubmit={addRoom} className="grid gap-3 md:grid-cols-4"><input required className="input" type="number" min="1" placeholder="Floor number" value={newRoom.floor} onChange={(event) => setNewRoom({ ...newRoom, floor: event.target.value })} /><input required className="input" placeholder="Room number e.g. 303" value={newRoom.number} onChange={(event) => setNewRoom({ ...newRoom, number: event.target.value })} /><input required className="input" type="number" min="0" placeholder="Bedroom beds" value={newRoom.bedroom_capacity} onChange={(event) => setNewRoom({ ...newRoom, bedroom_capacity: event.target.value })} /><input required className="input" type="number" min="0" placeholder="Hall beds" value={newRoom.hall_capacity} onChange={(event) => setNewRoom({ ...newRoom, hall_capacity: event.target.value })} /><button className="btn-primary md:col-span-4"><Plus size={16} /> Add New Room</button></form></DashboardModal>}</Page>;
}

function RoomDetail() {
  const { id } = useParams();
  const { data } = useFetch(`/rooms/${id}`, { slots: [] });
  const grouped = useMemo(() => ({ Bedroom: data.slots.filter((s) => s.area === "Bedroom"), Hall: data.slots.filter((s) => s.area === "Hall") }), [data]);
  return <Page title={`Room ${data.number || ""}`}><div className="grid gap-5 lg:grid-cols-2">{["Bedroom", "Hall"].map((area) => <section key={area} className="card p-4"><h2 className="font-bold">{area}</h2><div className="mt-3 grid gap-3">{grouped[area].map((slot) => <div key={slot.id} className="rounded-md border border-slate-100 p-3"><div className="flex items-center justify-between"><b>Slot {slot.code}</b><span className={`badge ${slot.is_occupied ? "bg-red-50 text-red-700" : "bg-emerald-50 text-emerald-700"}`}>{slot.is_occupied ? "Occupied" : "Vacant"}</span></div>{slot.student ? <p className="mt-2 text-sm">{slot.student.full_name}<br /><span className="text-slate-500">{slot.student.phone} - {slot.student.college_name}</span></p> : <p className="mt-2 text-sm text-slate-500">Available for allocation</p>}</div>)}</div></section>)}</div></Page>;
}

function Payments() {
  const { data: students } = useFetch("/students?status=Active", { students: [] });
  const { data: invoices, reload } = useFetch("/invoices", { invoices: [] });
  const { data: payments } = useFetch("/payments", { payments: [] });
  const [form, setForm] = useState({ method: "Cash", payment_date: currentDateTimeLocal() });
  const [sort, setSort] = useState("newest");
  const [historyStudent, setHistoryStudent] = useState(null);
  async function submit(e) {
    e.preventDefault();
    await api.post("/payments", form);
    setForm({ method: "Cash", payment_date: currentDateTimeLocal() });
    reload();
  }
  const groupedPayments = Object.values(payments.payments.reduce((groups, payment) => { const key = payment.student_id; (groups[key] ||= { student: payment.student, student_id: key, payments: [] }).payments.push(payment); return groups; }, {}));
  const sortedStudents = groupedPayments.sort((a, b) => { const aDate = a.payments.reduce((latest, payment) => payment.payment_date > latest ? payment.payment_date : latest, ""); const bDate = b.payments.reduce((latest, payment) => payment.payment_date > latest ? payment.payment_date : latest, ""); return sort === "newest" ? bDate.localeCompare(aDate) : aDate.localeCompare(bDate); });
  const history = historyStudent ? payments.payments.filter((payment) => payment.student_id === historyStudent.student_id).sort((a, b) => b.payment_date.localeCompare(a.payment_date)) : [];
  return <Page title="Rent Management"><section className="card p-4"><h2 className="font-bold">Record Payment</h2><form onSubmit={submit} className="mt-3 grid gap-3 md:grid-cols-7"><select required className="input" value={form.student_id || ""} onChange={(e) => setForm({ ...form, student_id: e.target.value })}><option value="">Student</option>{students.students.map((s) => <option key={s.id} value={s.id}>{s.full_name}</option>)}</select><select className="input" value={form.invoice_id || ""} onChange={(e) => setForm({ ...form, invoice_id: e.target.value })}><option value="">Current invoice</option>{invoices.invoices.map((i) => <option key={i.id} value={i.id}>{i.student} - {i.month} - {formatMoney(i.balance)}</option>)}</select><input required className="input" type="number" placeholder="Amount" value={form.amount || ""} onChange={(e) => setForm({ ...form, amount: e.target.value })} /><input className="input" placeholder="Transaction / Reference ID" value={form.transaction_id || ""} onChange={(e) => setForm({ ...form, transaction_id: e.target.value })} /><input required className="input" type="datetime-local" value={form.payment_date} onChange={(e) => setForm({ ...form, payment_date: e.target.value })} /><select className="input" value={form.method} onChange={(e) => setForm({ ...form, method: e.target.value })}>{["Cash", "UPI", "Bank Transfer", "Card", "Other"].map((m) => <option key={m}>{m}</option>)}</select><button className="btn-primary">Record</button></form></section><div className="mt-5 flex justify-end"><select className="input w-36" value={sort} onChange={(e) => setSort(e.target.value)}><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></div><DataList headers={["Student", "Transactions", "Latest Payment", "Total Paid"]}>{sortedStudents.map((student) => <tr key={student.student_id} className="mobile-row"><td><button className="font-semibold text-brand" onClick={() => setHistoryStudent(student)}>{student.student}</button></td><td>{student.payments.length}</td><td>{formatTimestamp(student.payments.reduce((latest, payment) => payment.payment_date > latest ? payment.payment_date : latest, ""))}</td><td>{formatMoney(student.payments.reduce((total, payment) => total + payment.amount, 0))}</td></tr>)}</DataList>{historyStudent && <DashboardModal title={`${historyStudent.student} Payment History`} onClose={() => setHistoryStudent(null)} search="" setSearch={() => {}}><DataList headers={["Date & Time", "Amount", "Method", "Transaction ID", "Status"]}>{history.map((payment) => <tr key={payment.id} className="mobile-row"><td>{formatTimestamp(payment.payment_date)}</td><td>{formatMoney(payment.amount)}</td><td>{payment.method}</td><td>{payment.transaction_id || "-"}</td><td>{payment.is_cancelled ? "Cancelled" : "Successful"}</td></tr>)}</DataList></DashboardModal>}</Page>;
}

function InvoiceTable({ invoices }) {
  return <DataList className="mt-5" headers={["Student", "Month", "Total", "Paid", "Balance", "Status"]}>{invoices.map((i) => <tr key={i.id} className="mobile-row"><td>{i.student}<br /><span className="text-xs text-slate-500">Room {i.room || "NA"}</span></td><td>{i.month}</td><td>{formatMoney(i.total_amount)}</td><td>{formatMoney(i.amount_paid)}</td><td>{formatMoney(i.balance)}</td><td><StatusBadge status={i.status} /></td></tr>)}</DataList>;
}

function StatusBadge({ status }) {
  const colors = { PAID: "bg-emerald-50 text-emerald-700", PARTIAL: "bg-orange-50 text-orange-700", OVERDUE: "bg-red-50 text-red-700", PENDING: "bg-slate-100 text-slate-700", Approved: "bg-emerald-50 text-emerald-700", Pending: "bg-slate-100 text-slate-700", Rejected: "bg-red-50 text-red-700", Out: "bg-orange-50 text-orange-700", Returned: "bg-emerald-50 text-emerald-700" };
  return <span className={`badge ${colors[status] || colors.PENDING}`}>{status}</span>;
}

function Dues() {
  const { data, reload } = useFetch("/dues", { dues: [] });
  const [pendingDelete, setPendingDelete] = useState(null);
  async function deleteStudent() {
    await api.delete(`/students/${pendingDelete.student_id}/unallocated`);
    setPendingDelete(null);
    reload();
  }
  return <Page title="Dues"><DataList headers={["Student", "Room", "Month", "Pending", "Due Date", "Status", "Actions"]}>{data.dues.map((d) => { const unallocated = !d.room || d.room === "NA" || d.roomAllocated === false || d.room_status === "unassigned"; return <tr key={d.id} className="mobile-row"><td>{d.student}</td><td>{d.room || "NA"}</td><td>{d.month}</td><td>{formatMoney(d.balance)}</td><td>{d.due_date}</td><td><StatusBadge status={d.status} /></td><td><div className="flex flex-wrap gap-2"><a className="btn-muted" href={whatsappLink({ full_name: d.student, phone: d.phone }, d.balance, d.month)} target="_blank">WhatsApp</a>{unallocated && <button className="btn-muted text-red-700" onClick={() => setPendingDelete(d)}><Trash2 size={14} /> Delete</button>}</div></td></tr>; })}</DataList>{pendingDelete && <ConfirmDialog title="Delete unallocated student?" message={`This will permanently remove ${pendingDelete.student} and their unallocated record.`} onCancel={() => setPendingDelete(null)} onConfirm={deleteStudent} />}</Page>;
}

function Expenses() {
  const { data, reload } = useFetch("/expenses", { expenses: [] });
  const [form, setForm] = useState({ category: "Food", payment_method: "Cash", expense_date: currentDateTimeLocal() });
  const [sort, setSort] = useState("newest");
  async function submit(e) {
    e.preventDefault();
    if (form.id) await api.put(`/expenses/${form.id}`, form);
    else await api.post("/expenses", form);
    setForm({ category: "Food", payment_method: "Cash", expense_date: currentDateTimeLocal() });
    reload();
  }
  async function del(expense) {
    if (!window.confirm(`Are you sure you want to delete this expense?\n\n${expense.category}\n${formatMoney(expense.amount)}\n${expense.expense_date}\n${expense.description || ""}`)) return;
    await api.delete(`/expenses/${expense.id}`, { data: { reason: "Deleted by admin" } });
    reload();
  }
  const sortedExpenses = [...data.expenses].sort((a, b) => sort === "newest" ? (b.expense_date || "").localeCompare(a.expense_date || "") : (a.expense_date || "").localeCompare(b.expense_date || ""));
  return <Page title="Expenses"><section className="card p-4"><h2 className="font-bold">{form.id ? "Edit Expense" : "Add Expense"}</h2><form onSubmit={submit} className="mt-3 grid gap-3 md:grid-cols-6"><input required className="input" type="datetime-local" value={form.expense_date || ""} onChange={(e) => setForm({ ...form, expense_date: e.target.value })} /><select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>{["Food", "Electricity", "Water", "Wi-Fi", "Cleaning", "Staff salary", "Maintenance", "Gas", "Repairs", "Washing machine", "Security", "Rent", "Other"].map((c) => <option key={c}>{c}</option>)}</select><input required className="input" type="number" placeholder="Amount" value={form.amount || ""} onChange={(e) => setForm({ ...form, amount: e.target.value })} /><input className="input" placeholder="Description" value={form.description || ""} onChange={(e) => setForm({ ...form, description: e.target.value })} /><input className="input" placeholder="Notes" value={form.notes || ""} onChange={(e) => setForm({ ...form, notes: e.target.value })} /><button className="btn-primary">Save</button></form></section><div className="mt-5 flex justify-end"><select className="input w-36" value={sort} onChange={(e) => setSort(e.target.value)}><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></div><DataList headers={["Timestamp", "Category", "Amount", "Method", "Description", "Actions"]}>{sortedExpenses.map((e) => <tr key={e.id} className="mobile-row"><td>{formatTimestamp(e.expense_date)}</td><td>{e.category}</td><td>{formatMoney(e.amount)}</td><td>{e.payment_method}</td><td>{e.description}</td><td><div className="flex gap-2"><button className="btn-muted" onClick={() => setForm({ ...e, expense_date: e.expense_date?.replace(" ", "T").slice(0, 16) })}><Edit size={14} /> Edit</button><button className="btn-muted text-red-700" onClick={() => del(e)}><Trash2 size={14} /> Delete</button></div></td></tr>)}</DataList></Page>;
}

function Outings() {
  const { data, reload } = useFetch("/outings", { outings: [], summary: {} });
  const [busy, setBusy] = useState(null);
  const [error, setError] = useState("");
  async function action(id, name) {
    setBusy(id); setError("");
    try { await api.post(`/outings/${id}/${name}`); await reload(); }
    catch (e) { setError(e.response?.data?.error || "Could not record movement"); }
    finally { setBusy(null); }
  }
  return <Page title="Outings">{error && <p role="alert" className="text-red-700">{error}</p>}<div className="mb-5 grid gap-3 sm:grid-cols-4">{[["Total Today", "total"], ["Approved", "approved"], ["Currently Out", "currently_out"], ["Returned", "returned"]].map(([label, key]) => <Stat key={key} label={label} value={data.summary[key]} icon={DoorOpen} />)}</div><DataList headers={["Student", "Room", "Date", "Destination", "Expected", "Departure", "Arrival", "Status", "Actions"]}>{data.outings.map(o => <tr key={o.id} className="mobile-row"><td>{o.student}</td><td>{o.room}</td><td>{o.outing_date}</td><td>{o.destination}</td><td>{o.expected_return_time}</td><td>{formatTimestamp(o.actual_leaving_time)}</td><td>{formatTimestamp(o.actual_return_time)}</td><td><StatusBadge status={o.status} /></td><td><div className="flex flex-wrap gap-2">{(o.status === "Pending" ? [["approve", "Approve"], ["reject", "Reject"]] : o.status === "Approved" ? [["out", "Record Outing"]] : ["Out", "Currently Out", "Late"].includes(o.status) ? [["returned", "Record Return"]] : []).map(([name, label]) => <button key={name} disabled={busy !== null} className="btn-muted" onClick={() => action(o.id, name)}>{label}</button>)}</div></td></tr>)}</DataList></Page>;
}

function Complaints({ student = false }) {
  const { data, reload } = useFetch(student ? "/complaints" : "/admin/complaints", { complaints: [] });
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ category: "Maintenance", priority: "MEDIUM", subject: "", description: "" });
  const [attachment, setAttachment] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [newCount, setNewCount] = useState(0);
  const [live, setLive] = useState(false);
  useEffect(() => setItems(data.complaints || []), [data.complaints]);
  useEffect(() => {
    const controller = new AbortController();
    let retryTimer;
    let knownIds = null;
    async function connect() {
      try {
        const response = await fetch(`${api.defaults.baseURL}/complaints/stream`, {
          headers: { Authorization: `Bearer ${localStorage.getItem("jtbh_token")}` }, signal: controller.signal
        });
        if (!response.ok) throw new Error("Complaint stream unavailable");
        setLive(true);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        while (!controller.signal.aborted) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          let divider;
          while ((divider = buffer.indexOf("\n\n")) >= 0) {
            const event = buffer.slice(0, divider); buffer = buffer.slice(divider + 2);
            if (!event.startsWith("data: ")) continue;
            const next = JSON.parse(event.slice(6)).complaints || [];
            const added = knownIds ? next.filter((complaint) => !knownIds.has(complaint.id)).length : 0;
            if (added) setNewCount((count) => count + added);
            knownIds = new Set(next.map((complaint) => complaint.id));
            setItems(next);
          }
        }
      } catch (streamError) { if (!controller.signal.aborted) setLive(false); }
      if (!controller.signal.aborted) retryTimer = setTimeout(connect, 2000);
    }
    connect();
    return () => { controller.abort(); clearTimeout(retryTimer); };
  }, [student]);
  async function submit(e) {
    e.preventDefault(); setBusy(true); setError("");
    try {
      const payload = attachment ? (() => { const value = new FormData(); Object.entries(form).forEach(([key, item]) => value.append(key, item)); value.append("attachment", attachment); return value; })() : form;
      await api.post("/complaints", payload);
      setForm({ category: "Maintenance", priority: "MEDIUM", subject: "", description: "" });
      setAttachment(null);
      await reload();
    } catch (e) { setError(e.response?.data?.error || "Could not submit complaint"); }
    finally { setBusy(false); }
  }
  async function update(id, status) {
    try { await api.patch(`/admin/complaints/${id}`, { status }); await reload(); }
    catch (e) { setError(e.response?.data?.error || "Could not update complaint"); }
  }
  async function followUp(id) {
    const message = window.prompt("Add a follow-up message");
    if (!message?.trim()) return;
    try { await api.post(`/complaints/${id}/follow-ups`, { message }); await reload(); }
    catch (e) { setError(e.response?.data?.error || "Could not add follow-up"); }
  }
  return <Page title={student ? "Raise a Complaint" : "Complaint Management"} action={!student && <div className="flex items-center gap-3"><span className={`text-sm ${live ? "text-emerald-700" : "text-slate-500"}`}>{live ? "Live updates on" : "Reconnecting..."}</span>{newCount > 0 && <button className="badge bg-red-100 text-red-700" onClick={() => setNewCount(0)}>{newCount} new</button>}</div>}>{error && <p role="alert" className="mb-3 text-red-700">{error}</p>}{student && <section className="card p-4"><h2 className="font-bold">Complaint Box</h2><form onSubmit={submit} className="mt-3 grid gap-3"><label>Category<select className="input" value={form.category} onChange={e => setForm({ ...form, category: e.target.value })}>{["Maintenance", "Electrical", "Plumbing", "Wi-Fi", "Food", "Cleaning", "Security", "Other"].map(category => <option key={category}>{category}</option>)}</select></label><label>Subject<input required maxLength={255} className="input" value={form.subject} onChange={e => setForm({ ...form, subject: e.target.value })} /></label><label>Description<textarea required rows={4} className="input" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} /></label><label>Supporting image/document (optional)<input className="input" type="file" accept="image/*,.pdf,.doc,.docx" onChange={e => setAttachment(e.target.files?.[0] || null)} /></label><button disabled={busy} className="btn-primary">{busy ? "Submitting..." : "Submit Complaint"}</button></form></section>}<h2 className="mt-5 font-bold">{student ? "My Complaints" : "Recent Complaints"}</h2><DataList className="mt-3" headers={student ? ["ID", "Category", "Subject", "Status", "Assigned / Response", "Updated"] : ["Student", "Room", "ID", "Category", "Subject", "Status", "Assigned / Response", "Updated"]}>{items.map(c => <tr key={c.id} className="mobile-row">{!student && <><td>{c.student}</td><td>{c.room || "Unallocated"}</td></>}<td>{c.complaint_no}</td><td>{c.category}</td><td><b>{c.subject}</b><br /><span className="text-xs text-slate-500">{c.description}</span></td><td>{student ? <StatusBadge status={c.status} /> : <select aria-label={`Status for ${c.subject}`} className="input" value={c.status} onChange={e => update(c.id, e.target.value)}>{["SUBMITTED", "UNDER_REVIEW", "IN_PROGRESS", "RESOLVED", "CLOSED"].map(status => <option key={status}>{status.replaceAll("_", " ")}</option>)}</select>}</td><td>{c.assigned_to || "Unassigned"}{c.admin_response && <><br /><span className="text-xs text-slate-500">{c.admin_response}</span></>}{student && !["RESOLVED", "CLOSED"].includes(c.status) && <button className="btn-muted mt-2" onClick={() => followUp(c.id)}>Add follow-up</button>}</td><td>{formatTimestamp(c.last_updated_at)}</td></tr>)}</DataList>{!items.length && <p className="p-4 text-slate-500">No complaints yet.</p>}</Page>;
}

function StudentProfile() {
  const { id } = useParams();
  const { data, reload } = useFetch(`/students/${id}`, { student: {}, invoices: [], payments: [], allocations: [] });
  const s = data.student;
  const [joiningDate, setJoiningDate] = useState("");
  useEffect(() => setJoiningDate(s.joining_date?.replace(" ", "T").slice(0, 16) || ""), [s.joining_date]);
  async function updateJoiningDate(e) {
    e.preventDefault();
    await api.put(`/students/${id}`, { joining_date: joiningDate });
    reload();
  }
  return <Page title={s.full_name || "Student"} action={<Link className="btn-primary" to="/payments"><CreditCard size={16} /> Record Payment</Link>}><section className="card p-5"><p className="text-sm text-slate-500">{s.student_code}</p><p className="mt-2 text-sm text-slate-600">Joined: {formatTimestamp(s.joining_date)} | Record created: {formatTimestamp(s.created_at)}</p><form onSubmit={updateJoiningDate} className="mt-3 flex flex-wrap items-end gap-3"><label className="text-sm font-semibold">Joining date and time<input required className="input mt-1 w-64" type="datetime-local" value={joiningDate} onChange={(e) => setJoiningDate(e.target.value)} /></label><button className="btn-muted">Update Date</button></form><div className="mt-4 grid gap-3 md:grid-cols-4"><Stat label="Room" value={s.room || "Unallocated"} icon={Building2} /><Stat label="Slot" value={s.slot || "NA"} icon={BedDouble} /><Stat label="Rent" value={formatMoney(s.monthly_rent)} icon={IndianRupee} /><Stat label="Balance" value={formatMoney(s.balance)} icon={Receipt} /></div></section><InvoiceTable invoices={data.invoices} /></Page>;
}

function Reports() {
  const { data } = useFetch("/reports/summary", { summary: {}, students: [], rooms: [] });
  const students = [...data.students].sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""));
  async function downloadReport() {
    const response = await api.get("/reports/export.csv", { responseType: "blob" });
    const url = URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = "jtbh-financial-report.csv";
    link.click();
    URL.revokeObjectURL(url);
  }
  return <Page title="Reports" action={<button className="btn-primary" onClick={downloadReport}><Download size={16} /> Export CSV</button>}><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"><Stat label="Current Residents" value={data.students.filter((s) => s.status === "Active").length} icon={Users} /><Stat label="Vacant Slots" value={data.summary.available_slots} icon={BedDouble} /><Stat label="Pending Dues" value={formatMoney(data.summary.pending_amount)} icon={Receipt} /></div><DataList className="mt-5" headers={["Student", "Joined", "Created"]}>{students.map((s) => <tr key={s.id} className="mobile-row"><td>{s.full_name}<br /><span className="text-xs text-slate-500">{s.student_code}</span></td><td>{formatTimestamp(s.joining_date)}</td><td>{formatTimestamp(s.created_at)}</td></tr>)}</DataList></Page>;
}

function SmallInfo({ label, value }) {
  return <div><p className="text-xs uppercase text-slate-500">{label}</p><p className="mt-1 font-semibold">{value}</p></div>;
}

function StudentHome() {
  const { data } = useFetch("/student/dashboard", { student: {}, latest_invoice: null, announcements: [] });
  const s = data.student;
  const inv = data.latest_invoice;
  return <Page title={`Hello, ${s.full_name || "Student"}`}><div className="grid gap-3 sm:grid-cols-2"><Stat label="Room" value={s.room || "Unallocated"} icon={Building2} /><Stat label="Floor" value={s.floor || "NA"} icon={Building2} /><Stat label="Slot" value={`${s.area || ""} ${s.slot || ""}`} icon={BedDouble} /><Link to="/student/payments" className="block"><Stat label="Monthly Rent" value={formatMoney(s.monthly_rent)} icon={IndianRupee} /></Link><Link to="/student/complaints" className="block"><Stat label="Complaints" value="Raise & Track" icon={MessageSquareWarning} /></Link><Link to="/student/notifications" className="block"><Stat label="Notifications" value="View Updates" icon={Bell} /></Link><Stat label="Current Due" value={formatMoney(s.balance)} icon={Receipt} /><Stat label="Payment Status" value={inv?.status || "PENDING"} icon={CreditCard} /></div><section className="card mt-5 p-4"><h2 className="font-bold">Announcements</h2><div className="mt-3 space-y-3">{data.announcements.map((a) => <div key={a.id} className="rounded-md bg-slate-50 p-3"><b>{a.title}</b><p className="text-sm text-slate-600">{a.message}</p></div>)}</div></section></Page>;
}

function StudentPayments() {
  const { data } = useFetch("/student/dashboard", { invoices: [], payments: [] });
  const [error, setError] = useState("");
  const [status, setStatus] = useState("ALL");
  const [month, setMonth] = useState("");
  async function receipt(payment) {
    try {
      const response = await api.get(`/payments/${payment.id}/receipt.pdf`, { responseType: "blob" });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a"); link.href = url; link.download = `${payment.receipt_no}.pdf`; link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch { setError("Could not download receipt. Please try again."); }
  }
  const rows = data.invoices.map((invoice) => { const payments = data.payments.filter((payment) => payment.invoice_id === invoice.id); const latest = payments[0]; const paymentStatus = latest?.is_cancelled ? "FAILED" : invoice.status; return { ...invoice, payment: latest, paymentStatus }; }).filter((row) => (status === "ALL" || row.paymentStatus === status) && (!month || row.month === month));
  const paid = data.payments.filter((payment) => !payment.is_cancelled).reduce((sum, payment) => sum + payment.amount, 0);
  const outstanding = data.invoices.reduce((sum, invoice) => sum + invoice.balance, 0);
  const nextDue = data.invoices.filter((invoice) => invoice.balance > 0).sort((a, b) => a.due_date.localeCompare(b.due_date))[0]?.due_date || "-";
  return <Page title="Rent & Payment History">{error && <p role="alert" className="text-red-700">{error}</p>}<div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Stat label="Total Rent Paid" value={formatMoney(paid)} icon={Receipt} /><Stat label="Current Month Rent" value={formatMoney(data.latest_invoice?.total_amount || 0)} icon={IndianRupee} /><Stat label="Outstanding Amount" value={formatMoney(outstanding)} icon={CreditCard} /><Stat label="Next Due Date" value={nextDue} icon={Receipt} /></div><div className="mb-3 flex flex-wrap gap-3"><select className="input w-40" value={status} onChange={e => setStatus(e.target.value)}>{["ALL", "PAID", "PENDING", "FAILED", "OVERDUE"].map(value => <option key={value}>{value}</option>)}</select><input className="input w-44" type="month" value={month} onChange={e => setMonth(e.target.value)} /></div><DataList headers={["Billing Period", "Rent", "Due Date", "Paid On", "Method", "Reference ID", "Late Fee", "Total Paid", "Status", "Receipt"]}>{rows.map(row => <tr key={row.id} className="mobile-row"><td>{row.month}</td><td>{formatMoney(row.total_amount)}</td><td>{row.due_date}</td><td>{formatTimestamp(row.payment?.payment_date)}</td><td>{row.payment?.method || "-"}</td><td>{row.payment?.transaction_id || "-"}</td><td>{formatMoney(row.payment?.late_fee || 0)}</td><td>{formatMoney(row.amount_paid)}</td><td><StatusBadge status={row.paymentStatus} /></td><td>{row.payment && !row.payment.is_cancelled ? <button className="btn-muted" onClick={() => receipt(row.payment)}><Download size={16} /> Receipt</button> : "Available after payment"}</td></tr>)}</DataList>{!rows.length && <p className="p-4 text-slate-500">No rent transactions match these filters.</p>}</Page>;
}

function StudentOuting() {
  const { data, reload } = useFetch("/student/dashboard", { outings: [] });
  const [form, setForm] = useState({});
  async function submit(e) {
    e.preventDefault();
    await api.post("/outings", form);
    setForm({});
    reload();
  }
  return <Page title="Outing"><section className="card p-4"><form onSubmit={submit} className="grid gap-3 md:grid-cols-3"><input required className="input" type="date" value={form.outing_date || ""} onChange={(e) => setForm({ ...form, outing_date: e.target.value })} /><input required className="input" type="time" value={form.leaving_time || ""} onChange={(e) => setForm({ ...form, leaving_time: e.target.value })} /><input required className="input" type="time" value={form.expected_return_time || ""} onChange={(e) => setForm({ ...form, expected_return_time: e.target.value })} /><input required className="input" placeholder="Destination" value={form.destination || ""} onChange={(e) => setForm({ ...form, destination: e.target.value })} /><input required className="input" placeholder="Reason" value={form.reason || ""} onChange={(e) => setForm({ ...form, reason: e.target.value })} /><button className="btn-primary">Request Outing</button></form></section><DataList className="mt-5" headers={["Date", "Destination", "Expected", "Status"]}>{data.outings.map((o) => <tr key={o.id} className="mobile-row"><td>{o.outing_date}</td><td>{o.destination}</td><td>{o.expected_return_time}</td><td><StatusBadge status={o.status} /></td></tr>)}</DataList></Page>;
}

function StudentComplaints() {
  return <Complaints student />;
}

function StudentNotifications() {
  const { data } = useFetch("/notifications", { notifications: [] });
  return <Page title="Notifications"><section className="card divide-y divide-slate-100">{data.notifications.map((notification) => <div key={notification.id} className="p-4"><p className="font-semibold">{notification.message}</p><p className="mt-1 text-xs text-slate-500">{formatTimestamp(notification.created_at)}</p></div>)}{!data.notifications.length && <p className="p-4 text-slate-500">No notifications yet.</p>}</section></Page>;
}

function StudentProfileSelf() {
  const { data, reload } = useFetch("/student/dashboard", { student: {} });
  const [form, setForm] = useState({});
  const s = data.student;
  useEffect(() => setForm({ phone: s.phone || "", email: s.email || "" }), [s.phone, s.email]);
  async function submit(e) {
    e.preventDefault();
    await api.put("/student/profile", form);
    reload();
  }
  return <Page title="Profile"><section className="card grid gap-3 p-5 md:grid-cols-2"><SmallInfo label="Student Name" value={s.full_name} /><SmallInfo label="Student ID" value={s.student_code} /><SmallInfo label="College" value={s.college_name} /><SmallInfo label="Course" value={s.course} /><SmallInfo label="Room" value={s.room} /><SmallInfo label="Slot" value={`${s.area || ""} ${s.slot || ""}`} /><SmallInfo label="Guardian" value={s.guardian_name} /><SmallInfo label="Guardian Phone" value={s.guardian_phone} /></section><section className="card mt-5 p-5"><h2 className="font-bold">Edit Contact</h2><form onSubmit={submit} className="mt-3 grid gap-3 md:grid-cols-3"><input className="input" placeholder="Phone" value={form.phone || ""} onChange={(e) => setForm({ ...form, phone: e.target.value })} /><input className="input" placeholder="Email" value={form.email || ""} onChange={(e) => setForm({ ...form, email: e.target.value })} /><button className="btn-primary">Save</button></form></section></Page>;
}

export default App;
