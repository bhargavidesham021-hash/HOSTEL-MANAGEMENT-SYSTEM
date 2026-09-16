import axios from "axios";

function normaliseApiBaseUrl(value) {
  const baseUrl = value?.trim().replace(/\/+$/, "");
  if (!baseUrl) return "";
  // Accept either https://host or https://host/api. This prevents requests
  // such as https://host/api/api/me when the environment variable includes /api.
  return /(?:\/api)+$/i.test(baseUrl) ? baseUrl.replace(/(?:\/api)+$/i, "/api") : `${baseUrl}/api`;
}

// Local development can use Flask on port 5000. A deployed frontend must be
// given its deployed API URL through Vercel (or its build environment).
const configuredApiUrl = normaliseApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
export const apiBaseUrl = configuredApiUrl || (import.meta.env.DEV ? "http://localhost:5000/api" : "");

export const api = axios.create({
  baseURL: apiBaseUrl
});

export function errorMessage(error, fallback = "Unable to complete this request.") {
  const payload = error?.response?.data;
  const value = payload?.error ?? payload?.message ?? error?.message;
  if (typeof value === "string" && value.trim()) return value;
  if (value && typeof value === "object" && typeof value.message === "string") return value.message;
  if (!error?.response) return "Cannot reach the hostel server. Please check your connection and try again.";
  if (error.response.status >= 500) return "The hostel server could not complete this request. Please try again shortly.";
  return fallback;
}

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
