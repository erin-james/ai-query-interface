import Papa from "papaparse";

/**
 * Parses raw CSV text into an array of objects using PapaParse.
 * Assumes the first row contains headers.
 *
 * @param csvText - Raw CSV string
 * @returns Parsed array of records
 */
function parseCSV(csvText: string) {
  return Papa.parse(csvText, { header: true, skipEmptyLines: true }).data;
}

/**
 * Loads and parses multiple CSV files from the public directory.
 * Returns a dictionary of arrays keyed by lowercase filenames.
 * Logs sample data for inspection.
 *
 * @returns A record of parsed CSV data for Customers, Detail, Inventory, and Pricelist
 */
export async function loadData() {
  const files = ["Customers", "Detail", "Inventory", "Pricelist"];
  const data: Record<string, any[]> = {};

  for (const name of files) {
    try {
      const response = await fetch(`/${name}.csv`);
      const text = await response.text();
      data[name.toLowerCase()] = parseCSV(text);
    } catch (err) {
      console.error(`Error loading ${name}.csv:`, err);
      data[name.toLowerCase()] = [];
    }
  }

  // Log sample rows for debugging
  console.log("Customers sample:", data.customers.slice(0, 3));
  console.log("Inventory sample:", data.inventory.slice(0, 3));
  console.log("Details sample:", data.detail.slice(0, 3));
  console.log("Pricelist sample:", data.pricelist.slice(0, 3));

  return data;
}
