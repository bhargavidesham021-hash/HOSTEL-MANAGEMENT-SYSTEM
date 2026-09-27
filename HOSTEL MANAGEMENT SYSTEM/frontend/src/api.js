import axios from "axios";

function normaliseApiBaseUrl(value) {
  const trimmed = value?.trim().replace(/^\/(https?:\/\/)/i, "$1");
  const baseUrl = trimmed?.replace(/\/+$/, "");
  if (!baseUrl) return "";
  // Accept either https://host or https://host/api. This prevents requests
  // such as https://host/api/api/me when the environment variable includes /api.
  return /(?:\/api)+$/i.test(baseUrl) ? baseUrl.replace(/(?:\/api)+$/i, "/api") : `${baseUrl}/api`;
}

// Every environment reads its API URL from Vite configuration. The local
// .env.example supplies the development URL; production builds get their own.
const configuredApiUrl = normaliseApiBaseUrl(import.meta.env.VITE_API_BASE_URL);
// Deployed builds default to the same-origin Flask API. Local development uses
// frontend/.env.example to point at the separately-running Flask dev server.
export const apiBaseUrl = configuredApiUrl || (import.meta.env.PROD ? "/api" : "");

export const api = axios.create({
  baseURL: apiBaseUrl
});

export function errorMessage(error, fallback = "Unable to complete this request.") {
  const payload = error?.response?.data;
  if (error?.response?.status === 405) return "The hostel API rejected this request. Check the deployment routing and try again.";
  const value = payload?.error ?? payload?.message ?? error?.message;
  if (typeof value === "string" && value.trim()) return value;
  if (value && typeof value === "object" && typeof value.message === "string") return value.message;
  if (!error?.response) return "Cannot reach the hostel server. Please check your connection and try again.";
  if (error.response.status >= 500) return "The hostel server could not complete this request. Please try again shortly.";
  return fallback;
}

api.interceptors.request.use((config) => {
  if (!apiBaseUrl) {
    return Promise.reject(new Error("The local API URL is not configured. Set VITE_API_BASE_URL=http://localhost:5000/api in frontend/.env."));
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
