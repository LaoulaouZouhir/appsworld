const resultEl = document.getElementById("result");
const statusText = document.getElementById("status-text");
const clearButton = document.getElementById("clear-result");

const forms = document.querySelectorAll("form[data-action]");

for (const form of forms) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    await executeAction(form);
  });
}

clearButton.addEventListener("click", () => {
  resultEl.textContent = "";
  statusText.textContent = "Ready";
});

async function executeAction(form) {
  const action = form.dataset.action;
  const formData = new FormData(form);

  const params = new URLSearchParams({ action });
  for (const [key, value] of formData.entries()) {
    if (value !== "") {
      params.append(key, value.toString());
    }
  }

  statusText.textContent = "Running…";

  try {
    const response = await fetch(`/api/index?${params.toString()}`);
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Unknown error");
    }

    resultEl.textContent = JSON.stringify(payload.data, null, 2);
    statusText.textContent = "Completed";
  } catch (error) {
    resultEl.textContent = JSON.stringify(
      {
        error: error.message,
      },
      null,
      2,
    );
    statusText.textContent = "Failed";
  }
}
