var stripe = Stripe("pk_test_51PwMLLE96mrdqv9LFinK9GuAsQPIzr1iV7G846ih3zO0UZBvQbuqyPdH5IOXhF3Fz7jJroviE3cHtK8nUaqYiKOy00SxdhPpAe");

        document.getElementById("checkout-button").addEventListener("click", function () {
            let lugar = document.getElementById("lugar").value;
            let distancia = document.getElementById("distancia").value;
            let hora = document.getElementById("hora").value;
            let servico = document.getElementById("servico").value;
            let preco = document.getElementById("preco").value;

            if (!lugar || !distancia || !hora || !preco || !servico) {
                alert("Por favor, preencha todos os campos.");
                return;
            }

            fetch("/stripe_payment/create-checkout-session/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")  // Proteção CSRF se necessário
                },
                body: JSON.stringify({
                    place: lugar,
                    distance: distancia,
                    time: hora,
                    service: servico,
                    preco: preco
                })
            })
            .then(response => response.json())
            .then(session => {
                if (session.error) {
                    alert("Erro ao criar sessão de pagamento: " + session.error);
                } else {
                    return stripe.redirectToCheckout({ sessionId: session.id });
                }
            })
            .catch(error => console.error("Erro:", error));
        });

        // Função para pegar o CSRF token do cookie
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                let cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    let cookie = cookies[i].trim();
                    if (cookie.startsWith(name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }