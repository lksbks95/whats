// No início do arquivo, adicione a importação do Picker e do ícone de emoji
import { Smile } from 'lucide-react'; // Adicione o ícone Smile
import Picker from 'emoji-picker-react'; // Importe o seletor de emojis

const ChatInterface = () => {
  // ... (seus outros estados)

  // --- NOVO ESTADO PARA O SELETOR DE EMOJIS ---
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

  // ... (resto das suas funções)

  // --- NOVA FUNÇÃO PARA QUANDO UM EMOJI É CLICADO ---
  const onEmojiClick = (emojiObject) => {
    setNewMessage(prevMessage => prevMessage + emojiObject.emoji);
    setShowEmojiPicker(false); // Fecha o seletor após escolher um emoji
  };


  return (
    <div className="flex h-screen bg-gray-50">
      {/* ... (código da lista de conversas e do chat) ... */}
      
      {/* Input de Mensagem */}
      <div className="bg-white border-t border-gray-200 p-4 relative"> {/* Adicionado 'relative' aqui */}
        
        {/* --- SELETOR DE EMOJIS (só aparece quando showEmojiPicker é true) --- */}
        {showEmojiPicker && (
          <div className="absolute bottom-20"> {/* Posiciona o seletor acima do input */}
            <Picker onEmojiClick={onEmojiClick} />
          </div>
        )}
        
        {/* ... (código da pré-visualização de arquivos) ... */}
        
        <div className="flex items-center space-x-2">
          {/* BOTÃO PARA ABRIR O SELETOR DE EMOJIS */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
          >
            <Smile className="h-4 w-4" />
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            <Paperclip className="h-4 w-4" />
          </Button>
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Digite sua mensagem..."
            className="flex-1"
            disabled={isUploading}
          />
          <Button onClick={sendMessage} disabled={(!newMessage.trim() && selectedFiles.length === 0) || isUploading}>
            {isUploading ? <Loader2 className="h-4 w-4 animate-spin"/> : <Send className="h-4 w-4" />}
          </Button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          multiple 
          onChange={handleFileSelect}
          accept="image/*,audio/*,.pdf,.doc,.docx,.txt,.xls,.xlsx"
        />
      </div>
    </div>
  );
};
