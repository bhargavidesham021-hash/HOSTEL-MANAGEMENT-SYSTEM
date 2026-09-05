import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api"
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("jtbh_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export function formatMoney(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);
}

export function whatsappLink(student, amount, month) {
  const phone = (student.phone || "").replace(/\D/g, "");
  const message = `Hello ${student.full_name},\n\nYour hostel payment of ${formatMoney(amount)} is pending for ${month}.\n\nPlease complete the payment.\n\nJai Tulja Bhavani Deluxe Boys Hostel\nNear Aurora College, Aushapur\nContact: 9822222064`;
  return `https://wa.me/91${phone.slice(-10)}?text=${encodeURIComponent(message)}`;
}
