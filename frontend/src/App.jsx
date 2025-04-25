import { Routes, Route } from "react-router"
import { ConfirmLocation } from "./pages/ConfirmLocation";
import { Welcome } from "./pages/Welcome";


function App() {
  return (
    <>
      <Routes>
        <Route path="/confirm" element={<ConfirmLocation />} />
        <Route path="/" element={<Welcome />} />
      </Routes>

    </>
  );
}

export default App;
