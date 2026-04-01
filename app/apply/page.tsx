// import ApplyPage from "./ApplyPage";

// export default function Page() {
//   return <ApplyPage />;
// }

import { Suspense } from "react";
import ApplyClient from "./ApplyPage";

export default function Page() {
  return (
    <Suspense fallback={<div className="p-6 text-center">Loading...</div>}>
      <ApplyClient />
    </Suspense>
  );
}