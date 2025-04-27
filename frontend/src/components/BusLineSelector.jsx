import { useState, useEffect } from "react";
import { fetchBusLines } from "../services/bus";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { formatISO, subMinutes } from "date-fns";
import { useLocation } from "../context/location";
import { createAlert } from "../services/alerts";

const schema = yup
  .object({
    line: yup.string().required("Selecione a linha"),
    email: yup
      .string()
      .email("E-mail precisa ser válido")
      .required("Digite seu E-mail"),
    datetime: yup.string().required("Selecione uma data"),
  })
  .required();

const errorClass = "text-red-700 text-sm font-bold relative top-0";
const inputClass =
  "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500";

export const BusLineSelector = () => {
  const [lines, setLines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLine, setSelectedLine] = useState("");

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null); // 'success' or null
  const [submitError, setSubmitError] = useState(null); // Error message string or null

  const { busStopLocation } = useLocation();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: yupResolver(schema) });
  const onSubmit = async (data) => {
    setIsSubmitting(true);
    setSubmitStatus(null);
    setSubmitError(null);

    if (!busStopLocation || !busStopLocation.lat || !busStopLocation.lng) {
      setSubmitError("Bus stop location is missing.");
      setIsSubmitting(false);
      return;
    }

    try {
      // 1. Prepare dates
      const endDate = data.datetime; // JS Date object from form
      const startDate = subMinutes(endDate, 30);
      const time_window_end_iso = formatISO(endDate);
      const time_window_start_iso = formatISO(startDate);

      // 2. Construct payload for the backend
      const payload = {
        user_email: data.email,
        // Handle single line for now based on previous model example
        // If form allows multiple lines, adjust data.line handling
        bus_line: data.line,
        stop_latitude: busStopLocation.lat,
        stop_longitude: busStopLocation.lng,
        time_window_start: time_window_start_iso,
        time_window_end: time_window_end_iso,
        alert_active: true, // Defaulting to active
      };
      console.log("Sending payload:", payload);

      // 3. Call the API service function
      const createdAlert = await createAlert(payload);
      console.log("Alert created:", createdAlert);
      setSubmitStatus("Alert created successfully!");
    } catch (error) {
      console.error("Failed to submit alert:", error);
      setSubmitError(
        error.response?.data?.detail ||
          "Failed to create alert. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    const getLines = async () => {
      try {
        setLoading(true);
        setError(null);
        const fetchedLines = await fetchBusLines();
        // Assuming fetchedLines is an array like ["665", "919"]
        setLines(fetchedLines || []); // Ensure it's an array
      } catch (err) {
        setError("Failed to load bus lines.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getLines();
  }, []); // Empty dependency array means run once on mount

  const handleSelectionChange = (event) => {
    setSelectedLine(event.target.value);
    console.log("Selected line:", event.target.value);
  };

  if (loading) {
    return <div>Loading bus lines...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>Error: {error}</div>;
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col p-5 items-center gap-1"
    >
      <label>Selecione a Linha</label>
      <select
        {...register("line")}
        id="bus-line-select"
        value={selectedLine}
        onChange={handleSelectionChange}
        disabled={lines.length === 0} // Disable if no lines loaded
        className={inputClass}
      >
        {lines.map((line) => (
          <option key={line} value={line}>
            {line} {/* Display the line number */}
          </option>
        ))}
      </select>
      <p className={errorClass}>{errors.line?.message}</p>
      <label htmlFor="">E-mail</label>
      <input className={inputClass} type="text" {...register("email")} />
      <p className={errorClass}>{errors.email?.message}</p>
      <label htmlFor="">Horário de Saída</label>
      <input
        className={inputClass}
        type="datetime-local"
        {...register("datetime")}
      />
      <p className={errorClass}>{errors.datetime?.message}</p>
      {lines.length === 0 && !loading && <div>No bus lines available.</div>}

      <button
        type="submit"
        disabled={isSubmitting}
        className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
      >
        {isSubmitting ? "Criando alerta..." : "Criar Alerta"}
      </button>
      {submitStatus && <div className="text-green-700">{submitStatus}</div>}
      {submitError && <div className="text-red-700">Error: {submitError}</div>}
    </form>
  );
};

export default BusLineSelector;
