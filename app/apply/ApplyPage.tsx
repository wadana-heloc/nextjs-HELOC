"use client";

import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { FieldLabel } from "@/components/ui/FieldLabel";
import { HelpText } from "@/components/ui/HelpText";
import { useRouter } from "next/navigation";

export default function ApplyPage() {
  const params = useSearchParams();
  const router = useRouter();
  // Prefill values from calculator
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [emiratesId, setEmiratesId] = useState("");
  const [phone, setPhone] = useState("");

  const [community, setCommunity] = useState(
    params.get("community") || ""
  );
  const [propertyType, setPropertyType] = useState(
    params.get("propertyType") || ""
  );
  const [sizeSqft, setSizeSqft] = useState(
    params.get("sizeSqft") || ""
  );

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);


  //function that handels the form submission. It sends a POST request to the backend API with the form data. If the request is successful, it shows a success message. If there's an error, it shows an error message.
  async function handleSubmit() {

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/applications`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            full_name: fullName,
            email,
            emirates_id: emiratesId,
            phone,
            community,
            property_type: propertyType,
            size_sqft: Number(sizeSqft),
          }),
        }
      );

      if (!res.ok) {
        throw new Error("Failed to submit application");
      }

      setSuccess(true);
          const data = await res.json();
    // 👉 redirect to result page with id
    console.log("Application ID:", data.id);
    router.push(`/application-status?id=${data.id}&status=${data.status}`);

    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // if (success) {
  //   return (
  //     <div className="min-h-screen flex items-center justify-center">
  //       <div className="bg-green-50 border border-green-200 p-6 rounded-xl">
  //         <h2 className="text-lg font-semibold text-green-800">
  //           {/* Application submitted successfully 🎉 */}
  //           Your application status : pending!
  //         </h2>
  //       </div>
  //     </div>
  //   );
  // }



  //UI for the application form. It includes fields for full name, email, Emirates ID, phone, community, property type, and size in sqft. There's also a submit button that triggers the handleSubmit function when clicked. If there's an error, it displays the error message below the button.
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="w-full max-w-xl bg-white p-6 rounded-2xl border shadow-sm">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Apply for Equity Access

        </h1>

        <div className="space-y-4">

          <div>
            <FieldLabel htmlFor="name">Full Name</FieldLabel>
            <input
              id="name"
              // className="mt-1 w-full border rounded-lg px-3 py-2"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="email">Email</FieldLabel>
            <input
              id="email"
              // className="mt-1 w-full border rounded-lg px-3 py-2"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"

              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="eid">Emirates ID</FieldLabel>
            <input
              id="eid"
              // className="mt-1 w-full border rounded-lg px-3 py-2"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"

              value={emiratesId}
              onChange={(e) => setEmiratesId(e.target.value)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="phone">Phone</FieldLabel>
            <input
              id="phone"
              // className="mt-1 w-full border rounded-lg px-3 py-2"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"

              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="community">Community</FieldLabel>
            <input
              id="community"
              // className="mt-1 w-full border rounded-lg px-3 py-2"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={community}
              onChange={(e) => setCommunity(e.target.value)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="type">Property Type</FieldLabel>
            <input
              id="type"
              // className="mt-1 w-full border rounded-lg px-3 py-2"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={propertyType}
              onChange={(e) => setPropertyType(e.target.value)}
            />
          </div>

          <div>
            <FieldLabel htmlFor="size">Size (sqft)</FieldLabel>
            <input
              id="size"
              // className="mt-1 w-full border rounded-lg px-3 py-2"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              value={sizeSqft}
              onChange={(e) => setSizeSqft(e.target.value)}
            />
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={loading}
            // className="w-full bg-slate-900 text-white py-2.5 rounded-lg mt-4"
            className="mt-2 w-full rounded-lg bg-slate-900 py-2.5 text-white font-medium hover:bg-slate-800 disabled:opacity-50 disabled:hover:bg-slate-900"
          >
            {loading ? "Submitting..." : "Submit Application"}
          </button>

          {error && (
            <div className="text-red-600 text-sm mt-2">
              {error}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}