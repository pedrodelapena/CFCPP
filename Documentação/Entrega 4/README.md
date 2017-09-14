# Projeto - Entrega 4

Esta etapa do projeto consiste dividir um arquivo em pacotes menores, facilitando a transmissão, a detecção de bits corrompidos e o consequente reenvio apenas dos pacotes corrompidos. A detecção de bits corrompidos ocorre pela implementação do CRC (Cyclic redundancy
 check) tanto no Head quanto no Payload.
<p>Para que a transmissão seja realizada, o servidor compara os CRCs e envia um ACK para o client caso o pacote esteja de acordo com o esperado ou um nACK, caso contrário.</p>
 
## Fragmentação

Nesta etapa, o payload é dividido em vários pacotes com <b>tamanho máximo</b> de 2048 bytes. A divisão faz com que:

<p>- O tempo da tranmissão torne-se menor devido à redução no tamanho dos pacotes, possibilitando que arquivos maiores, quando corrompidos, sejam mais facilmente corrigidos.</p>
<p>- O <i>Overhead</i> e consequentemente <i>Throughput</i> tornem-se maiores e o mesmo ocorre com a velocidade de transmissão dos dados. </p>
<p>- O payload não extrapole o tamanho máximo nos campos do Head, isto é, o tamanho pré definido garante que o número não passará de 16 bits e possibilita a formação bem sucedida do Head.</p>

## Head

Previamente, o Head continha apenas os campos:

<p>- start (8 bits)</p> 
<p>- size (16 bits)</p>
<p>- SYN (8 bits)</p> 
<p>- ACK/nACK (8 bits)</p>

Nesta etapa do projeto, foram adicionados os seguintes campos ao Head:

<p>- P_size (8 bits)</p>
<p>- P_total (8 bits)</p> 
<p>- CheckSum (16 bits)</p>
<p>- CheckSum_head (16 bits)</p>

onde P_size é o tamanho do pacote, P_total é o tamanho total dos pacotes, CheckSum_head é o CRC calculado para o Head e o CheckSum é o CRC calculado para o Payload.

## Polinômio utilizado para o CRC

O polinômio utilizado foi o CRC-16-IBM, também conhecido apenas como <b>CRC-16</b>. 


| <b>Forma do polinômio</b> | <b>Conteudo </b>   |
|-------------|--------------------|
| Hexadecimal |         0x18005    |
| Binária     |  11000000000000101 |
| Polinomial  | x^16+x^15+x^12+x^0 |

Em comparação com as outras formas de realizar o cálculo do CRC, o CRC-16 é o mais eficiente para o tamanho dos dados transmitidos: em uma sequência de 16 ou menos bits, 100% das falhas são reconhecidas pelo por este CRC. Já o CRC-32 seria menos eficiente para um pacote relativamente pequeno como o transmitido neste projeto, mesmo possuindo a mesma propriedade que o CRC-16 para um pacote de 16 ou menos bits.

## TimeOut

O tempo de timeout escolhido foi de 6s. O envio e recepção não são istantâneos, algumas partes do código demoram para rodar (prints) e quisemos ter uma margem de segurança. Além disso, um timeout menor fazia com que o pacote deixasse de ser recebido pelo server quando foi realizado o teste de validação <i>"Durante a transmissão, desconectar o fio que transmite dados entre Client e Server"</i>
