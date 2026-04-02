"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";

export default function ApplicationStatusClient() {
  const params = useSearchParams();
  const router = useRouter();

  const id = params.get("id");

  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchStatus() {
      if (!id) {
        setError("Invalid application ID.");
        setLoading(false);
        return;
      }

      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/applications/${id}`
        );

        if (!res.ok) {
          throw new Error("Failed to fetch application status.");
        }

        const data = await res.json();
        setStatus(data.status);
      } catch (err) {
        setError("Something went wrong while fetching status.");
      } finally {
        setLoading(false);
      }
    }

    fetchStatus();
  }, [id]);

  const getStatusColor = () => {
    if (status === "eligible") return "text-green-600";
    if (status === "pending") return "text-yellow-600";
    if (status === "rejected") return "text-red-600";
    return "text-slate-600";
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-slate-600">Loading application status...</p>
      </div>
    );
  }

  if (error) {
    return (

      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 p-6 rounded-xl text-center">
          <p className="text-red-600">{error}</p>

          <button
            onClick={() => router.push("/")}
            className="mt-4 w-full bg-slate-900 text-white py-2 rounded-lg"
          >
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
        {/* <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 flex items-center justify-center"> */}
      <div className="w-full max-w-md bg-white border p-6 rounded-2xl shadow-sm text-center space-y-4">
        <h1 className="text-2xl font-semibold text-slate-900">
          Application Status
        </h1>

        <p className={`text-lg font-medium ${getStatusColor()}`}>
          {status}
        </p>

        <button
          onClick={() => router.push("/")}
          className="w-full bg-slate-900 text-white py-2.5 rounded-lg font-medium hover:bg-slate-800"
        >
          Go to Home
        </button>

        {status === "eligible" && (
          <button
            onClick={() => router.push("/next-step")}
            className="w-full bg-green-600 text-white py-2.5 rounded-lg font-medium hover:bg-green-700"
          >
            Continue Application
          </button>
        )}
      </div>
    </div>
  );
}