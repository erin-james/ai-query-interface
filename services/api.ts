import axios from 'axios';



const BASE_IP = "xxx.xxx.x.xx"; //replace with your local ip address
const PORT = 8000;
const ENDPOINT = "query";

const BASE_URL  = `http://${BASE_IP}:${PORT}/${ENDPOINT}`;


/**
 * Sends a GET request to the FastAPI backend with a natural language question.
 * Returns the parsed answer string from the response, or a fallback error message.
 *
 * @param question - A natural language query about CSV data (e.g. "top customer", "items over $50")
 * @returns A string response from the backend, formatted for display in the chat UI
 */
export const queryCSV = async (question: string): Promise<string> => {
  try {
    const response = await axios.get(BASE_URL, {
      params: { question },
    });
    return response.data.answer;
  } catch (error) {
    console.error('API error:', error);
    return 'Sorry, something went wrong while querying the data.';
  }
};
