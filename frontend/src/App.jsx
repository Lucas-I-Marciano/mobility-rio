import { ConfirmLocation } from "./pages/ConfirmLocation";
import { Routes, Route } from "react-router"

function App() {
  return (
    <>
      <Routes>
        <Route path="/confirm" element={<ConfirmLocation />} />
      </Routes>

    </>
  );
}

export default App;
