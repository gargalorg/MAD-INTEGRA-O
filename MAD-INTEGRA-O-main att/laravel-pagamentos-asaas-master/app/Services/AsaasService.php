    /**
     * Pagamento com Split de Comissão
     */
    public function paymentWithSplit($data)
    {
        $data = json_encode([
            "externalReference" => $data['id'],
            "customer"          => $data['customer'],
            "billingType"       => $data['billing_type'],
            "dueDate"           => $data['due_date'],
            "value"             => $data['value'],
            "description"       => $data['description'],
            "split" => [
                [
                    "walletId"        => env('ASAAS_ADMIN_WALLET_ID'),
                    "percentualValue" => 90, // 90% para o admin
                    "fixedValue"      => null,
                    "description"     => "Admin"
                ],
                [
                    "walletId"        => env('ASAAS_PARTNER_WALLET_ID'),
                    "percentualValue" => 10, // 10% para o parceiro
                    "fixedValue"      => null,
                    "description"     => "Parceiro"
                ]
            ]
        ]);

        return asaasCurlSend(
            'POST',
            '/api/v3/payments',
            $data
        );
    }
}
