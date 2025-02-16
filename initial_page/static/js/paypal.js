document.getElementById("checkout-button").addEventListener("click", function () {
    fetch("/paypal_payment/create/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            preco: 5000,  // Valor em CVE
            service: "Transfer Aeroporto",
            place: "Praia",
            time: "2 horas",
            distance: "20 km"
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;  // Redireciona para PayPal
        } else {
            alert("Erro no pagamento: " + data.error);
        }
    })
    .catch(error => console.error("Erro:", error));
});

