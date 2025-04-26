import { Routes, Route } from "react-router"
import { ConfirmLocation } from "./pages/ConfirmLocation";
import { Welcome } from "./pages/Welcome";
import { ChoseBusStop } from "./pages/ChoseBusStop"


function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/confirm" element={<ConfirmLocation />} />
        <Route path="/bus" element={<ChoseBusStop />} />
      </Routes>

    </>
  );
}

export default App;
