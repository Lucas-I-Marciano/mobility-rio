import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { formatISO, subMinutes } from "date-fns";
import { createAlert } from "../services/alerts"; // Sua função de API
import { fetchBusLines } from "../services/bus";
import { sendConfirmationEmail } from "../services/notifications";
// Importe seu componente DatePicker favorito
// import DatePicker from "react-datepicker";
// import "react-datepicker/dist/react-datepicker.css";

const alertSchema = yup.object().shape({
  email: yup.string().email("Email inválido").required("Email é obrigatório"),
  line: yup.string().required("Linha de ônibus é obrigatória"), // Ajuste se for múltiplas linhas
  start_datetime: yup
    .date()
    .required("Data/Hora de início dos alertas é obrigatória")
    .typeError("Data/Hora inválida"),
});

export const AlertForm = ({ selectedBusStop, setSelectedLineCallback }) => {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
    reset,
  } = useForm({
    resolver: yupResolver(alertSchema),
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  const [busLines, setBusLines] = useState([]);
  const [isLinesLoading, setIsLinesLoading] = useState(true);
  const [linesError, setLinesError] = useState(null);

  useEffect(() => {
    const loadBusLines = async () => {
      setIsLinesLoading(true);
      setLinesError(null);
      try {
        const linesData = await fetchBusLines();
        // Ensure data is an array before setting
        setBusLines(Array.isArray(linesData) ? linesData : []);
      } catch (error) {
        setLinesError("Falha ao carregar linhas de ônibus.");
        console.error("Error fetching lines:", error);
        setBusLines([]); // Set empty on error
      } finally {
        setIsLinesLoading(false);
      }
    };
    loadBusLines();
  }, []);

  const handleLineChange = (event) => {
    const newLine = event.target.value;
    console.log("LINE SELECT - Calling setSelectedLineCallback with:", newLine); // <-- ADICIONE AQUI
    // Atualiza o estado 'line' no componente pai (ChoseBusStop)
    // Isso vai disparar o useEffect para buscar os dados da tabela/mapa
    if (setSelectedLineCallback) {
      setSelectedLineCallback(newLine || null); // Passa null se selecionar a opção vazia
    }
  };

  const onSubmitForm = async (data) => {
    setIsSubmitting(true);
    setSubmitStatus(null);
    setSubmitError(null);
    let alertCreatedSuccessfully = false;

    try {
      const endDate = data.start_datetime; // Data/Hora selecionada pelo usuário
      const startDate = subMinutes(endDate, 30); // 30 min antes

      const time_window_end_iso = formatISO(endDate);
      const time_window_start_iso = formatISO(startDate);
      // Define o timestamp de referência para o filtro da task (o início da janela)
      const start_alert_iso = time_window_start_iso;

      const payload = {
        user_email: data.email,
        bus_line: data.line, // Ajuste se precisar enviar lista: [data.line]
        stop_latitude: selectedBusStop.lat,
        stop_longitude: selectedBusStop.lng,
        time_window_start: time_window_start_iso,
        time_window_end: time_window_end_iso,
        start_alert_iso: start_alert_iso, // Campo novo adicionado
        alert_active: true,
      };

      console.log("Enviando Payload do Alerta:", payload);
      const createdAlert = await createAlert(payload);
      console.log("Alerta criado no backend:", createdAlert);
      setSubmitStatus(
        "Alerta criado com sucesso! Enviando email de confirmação..."
      );
      alertCreatedSuccessfully = true; // Marca sucesso

      // --- CHAMA A API DE CONFIRMAÇÃO APÓS SUCESSO ---
      if (createdAlert) {
        // Garante que temos os dados do alerta criado
        // Prepara dados para o email de confirmação
        // Precisamos dos objetos 'time' que foram validados
        // Se 'data' ainda tiver datetime, precisamos converter aqui ou pegar do createdAlert se ele retornar time
        let startTimeObj, endTimeObj;
        // Assumindo que data.start_datetime ainda é Date do picker
        const endDate = data.start_datetime;
        const startDate = subMinutes(endDate, 30);
        // Converte para time local SP (poderia ser uma função util)
        const saoPauloTZ =
          /* Obtenha ZoneInfo("America/Sao_Paulo") aqui ou importe */
          (startTimeObj = startDate
            .toLocaleTimeString("sv-SE", {
              timeZone: "America/Sao_Paulo",
              hour12: false,
            })
            .split(" ")[0]); // Formato HH:MM:SS
        endTimeObj = endDate
          .toLocaleTimeString("sv-SE", {
            timeZone: "America/Sao_Paulo",
            hour12: false,
          })
          .split(" ")[0];

        const confirmationPayload = {
          recipient_email: createdAlert.user_email, // Usa o email do alerta criado
          bus_line: createdAlert.bus_line,
          stop_lat: createdAlert.stop_latitude,
          stop_lng: createdAlert.stop_longitude,
          // Envia a HORA (formato HH:MM:SS esperado pelo Pydantic 'time')
          start_time: startTimeObj,
          end_time: endTimeObj,
        };

        try {
          console.log("Enviando payload de confirmação:", confirmationPayload);
          // Chama a nova função da API (não precisa de await se backend usa BackgroundTasks)
          await sendConfirmationEmail(confirmationPayload);
          console.log("Solicitação de email de confirmação enviada.");
          // Atualiza status para indicar sucesso completo
          setSubmitStatus("Alerta criado e email de confirmação solicitado!");
        } catch (emailError) {
          console.error("Falha ao solicitar email de confirmação:", emailError);
          // Informa o usuário, mas o alerta principal foi criado
          setSubmitStatus(
            "Alerta criado, mas falha ao enviar email de confirmação."
          );
        }
      }
      // --- FIM CHAMADA DE CONFIRMAÇÃO ---

      reset(); // Limpa o formulário
    } catch (error) {
      console.error("Falha ao criar alerta:", error);
      setSubmitError(
        error.response?.data?.detail ||
          "Falha ao criar alerta. Tente novamente."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-4">
      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-gray-700"
        >
          Email:
        </label>
        <input
          type="email"
          id="email"
          {...register("email")}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        {errors.email && (
          <p className="text-xs text-red-600 mt-1">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="line"
          className="block text-sm font-medium text-gray-700"
        >
          Linha de Ônibus:
        </label>
        <select
          id="line"
          {...register("line")}
          className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100"
          disabled={isLinesLoading || busLines.length === 0} // Disable while loading or if empty
          onChange={handleLineChange}
        >
          <option value="">
            {isLinesLoading
              ? "Carregando linhas..."
              : "-- Selecione uma linha --"}
          </option>
          {busLines.map((line) => (
            <option key={line} value={line}>
              {line}
            </option>
          ))}
        </select>
        {linesError && (
          <p className="text-xs text-red-600 mt-1">{linesError}</p>
        )}
        {!isLinesLoading && busLines.length === 0 && !linesError && (
          <p className="text-xs text-gray-500 mt-1">
            Nenhuma linha encontrada.
          </p>
        )}
        {errors.line && (
          <p className="text-xs text-red-600 mt-1">{errors.line.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="start_datetime"
          className="block text-sm font-medium text-gray-700"
        >
          Data/Hora de Início dos Alertas:
          <span className="text-xs text-gray-500">
            (O alerta será diário 30min antes deste horário)
          </span>
        </label>
        {/* --- Substitua pelo seu componente DatePicker --- */}
        {/* Exemplo com input simples (NÃO RECOMENDADO para UX, só para estrutura) */}
        <input
          type="datetime-local" // Use um DatePicker AQUI!
          id="start_datetime"
          {...register("start_datetime")} // react-hook-form pode precisar de <Controller> para date pickers
          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        {/* --- Fim da substituição --- */}
        {errors.start_datetime && (
          <p className="text-xs text-red-600 mt-1">
            {errors.start_datetime.message}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isSubmitting ? "Criando..." : "Criar Alerta"}
      </button>

      {submitStatus && (
        <p className="text-sm text-green-600 mt-2">{submitStatus}</p>
      )}
      {submitError && (
        <p className="text-sm text-red-600 mt-2">Erro: {submitError}</p>
      )}
    </form>
  );
};
