<?php
header('Content-Type: application/json; charset=utf-8');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(['ok'=>false]); exit; }

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) { $data = $_POST; }

$hp = trim($data['website'] ?? '');
if ($hp !== '') { echo json_encode(['ok'=>true]); exit; } // honeypot -> pretend success

$name    = trim($data['name'] ?? '');
$phone   = trim($data['phone'] ?? '');
$message = trim($data['message'] ?? ($data['comment'] ?? ''));

if ($name === '' || $phone === '') { http_response_code(400); echo json_encode(['ok'=>false,'error'=>'name and phone required']); exit; }

// --- 1) email via beget mail() ---
$to      = 'vyache.cuk@yandex.ru';
$subject = 'Новая заявка с сайта — ' . $name . ($phone ? ', ' . $phone : '');
$body    = "Новая заявка с сайта vetnasvyaz.ru:\n\n"
         . "Имя: $name\n"
         . "Телефон: $phone\n"
         . ($message ? "Сообщение: $message\n" : '')
         . "\nИсточник: сайт (форма обратной связи)";
$headers = "From: Ветеринар на связи <info@vetnasvyaz.ru>\r\n"
         . "Reply-To: info@vetnasvyaz.ru\r\n"
         . "MIME-Version: 1.0\r\n"
         . "Content-Type: text/plain; charset=UTF-8\r\n";
@mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers);

// --- 2) forward to Strapi for storage (best-effort) ---
$payload = json_encode(['data' => [
  'site' => 'vetnas', 'name' => $name, 'phone' => $phone,
  'comment' => $message, 'consent' => true, 'source' => 'site-form', 'status' => 'new',
]], JSON_UNESCAPED_UNICODE);
$ch = curl_init('https://deltamoscow.ru/cms/api/bookings');
curl_setopt_array($ch, [
  CURLOPT_POST => true,
  CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
  CURLOPT_POSTFIELDS => $payload,
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_TIMEOUT => 8,
]);
@curl_exec($ch);
@curl_close($ch);

echo json_encode(['ok'=>true]);
