document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formRelatorio");
    const tabelaDiv = document.getElementById("tabelaResultado");
    const resultadoCard = document.getElementById("resultadoRelatorio");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const data = {
            dataInicio: form.dataInicio.value,
            dataFim: form.dataFim.value,
            tipoRelatorio: form.tipoRelatorio.value,
            exportarPDF: document.getElementById("exportarPDF").checked,
        };

        // 🔹 Requisição ao backend para gerar o relatório
        const response = await fetch("/relatorios/gerar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        // Verifica se é PDF ou JSON
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/pdf")) {
            const confirmDownload = confirm("Deseja realmente baixar o PDF do relatório?");
            if (confirmDownload) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `relatorio_${data.tipoRelatorio}_${new Date().toISOString().slice(0,19)}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            }
            return;
        }

        const result = await response.json();

        // Exibe tabela
        renderTable(result.dados);
        resultadoCard.classList.remove("d-none");
    });

    function renderTable(rows) {
        if (!rows || rows.length === 0) {
            tabelaDiv.innerHTML = "<p class='text-muted'>Nenhum dado encontrado.</p>";
            return;
        }

        const headers = Object.keys(rows[0]);
        const table = `
            <table class="table table-striped table-hover">
                <thead class="table-primary">
                    <tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr>
                </thead>
                <tbody>
                    ${rows.map(r => `<tr>${headers.map(h => `<td>${r[h]}</td>`).join("")}</tr>`).join("")}
                </tbody>
            </table>
        `;
        tabelaDiv.innerHTML = table;
    }
});