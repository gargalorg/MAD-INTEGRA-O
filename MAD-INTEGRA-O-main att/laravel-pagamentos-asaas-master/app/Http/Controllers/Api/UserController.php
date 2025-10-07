<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use App\Services\AsaasService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;

class UserController extends Controller
{
    protected $asaas;

    public function __construct(AsaasService $asaas)
    {
        $this->asaas = $asaas;
    }

    /**
     * Cria usuário, cliente no Asaas e gera cobrança com split.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users,email',
            'cpf' => 'required|string|unique:users,cpf',
        ]);

        $user = User::create($validated);

        // Cria cliente no Asaas
        $customerId = $this->asaas->createCustomer($user);
        $user->update(['asaas_customer_id' => $customerId]);

        // Valor do pagamento (exemplo: R$ 100,00)
        $value = 100.00;

        // Split: 90% para admin e 10% para parceiro (IDs fictícios de contas)
        $split = [
            [
                'walletId' => env('ASAAS_ADMIN_WALLET_ID'),
                'fixedValue' => null,
                'percentualValue' => 90,
            ],
            [
                'walletId' => env('ASAAS_PARTNER_WALLET_ID'),
                'fixedValue' => null,
                'percentualValue' => 10,
            ]
        ];

        // Cria cobrança com split
        $payment = $this->asaas->createPaymentWithSplit($user, $value, $split);

        return response()->json([
            'message' => 'Usuário cadastrado e cobrança criada com sucesso.',
            'user' => $user,
            'payment' => $payment
        ]);
    }

    /**
     * Recebe webhook do Asaas e atualiza status do usuário.
     */
    public function webhook(Request $request)
    {
        Log::info('Webhook recebido:', $request->all());

        $event = $request->input('event');
        $payment = $request->input('payment');

        if (!$payment || empty($payment['customer'])) {
            return response()->json(['error' => 'Dados inválidos'], 400);
        }

        $user = User::where('asaas_customer_id', $payment['customer'])->first();
        if (!$user) return response()->json(['error' => 'Usuário não encontrado'], 404);

        switch ($event) {
            case 'PAYMENT_CONFIRMED':
                $user->update(['status' => 'ativo']);
                break;
            case 'PAYMENT_REFUNDED':
            case 'PAYMENT_OVERDUE':
            case 'PAYMENT_CANCELED':
                $user->update(['status' => 'cancelado']);
                break;
        }

        return response()->json(['success' => true]);
    }
}
