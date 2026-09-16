import axios from "axios";

// Local development can use Flask on port 5000. A deployed frontend must be
// given its deployed API URL through Vercel (or its build environment).
const configuredApiUrl = import.meta.env.VITE_API_BASE_URL?.trim();
export const apiBaseUrl = configuredApiUrl || (import.meta.env.DEV ? "http://localhost:5000/api" : "");

export const api = axios.create({
  baseURL: apiBaseUrl
});

api.interceptors.request.use((config) => {
  if (!apiBaseUrl) {
    return Promise.reject(new Error("The live site is not connected to its API. Set VITE_API_BASE_URL in the frontend deployment settings and redeploy."));
  }
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
