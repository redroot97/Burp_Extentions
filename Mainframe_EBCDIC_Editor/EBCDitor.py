from burp import IBurpExtender, IContextMenuFactory, IContextMenuInvocation
from javax.swing import JMenuItem, JOptionPane
from javax.swing import JTextArea, JScrollPane
import binascii
import codecs
import java.util.Arrays as Arrays
import array

class BurpExtender(IBurpExtender, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("EBCDIC Editor")
        callbacks.registerContextMenuFactory(self)
        print("EBCDIC to ASCII Converter extension loaded")

    def createMenuItems(self, invocation):
        menu = Arrays.asList(JMenuItem("Edit", actionPerformed=lambda x: self.convertEBCDICToASCII(invocation)))
        return menu

    def convertEBCDICToASCII(self, invocation):
        # Get the selected message
        messages = invocation.getSelectedMessages()
        if messages is None or len(messages) == 0:
            return
        
        # Get the selection bounds
        selection_bounds = invocation.getSelectionBounds()
        if selection_bounds is None or len(selection_bounds) != 2:
            return
        
        selected_message = messages[0]
        is_request = invocation.getInvocationContext() in [IContextMenuInvocation.CONTEXT_MESSAGE_EDITOR_REQUEST, IContextMenuInvocation.CONTEXT_MESSAGE_VIEWER_REQUEST]

        message_info = selected_message
        if not message_info:
            return
        
        raw_content = message_info.getRequest() if is_request else message_info.getResponse()

        # Select the raw content in bytes
        raw_content_bytes = array.array('b', raw_content)

        # Convert from bytes to the raw string using latin1
        selected_text = raw_content_bytes[selection_bounds[0]:selection_bounds[1]].tostring().decode('latin1')

        # Strip the last two characters
        if len(selected_text) > 2:
            stripped_chars = selected_text[-2:]
            selected_text = selected_text[:-2]
        else:
            stripped_chars = ''

        try:
            # Convert selected text to EBCDIC bytes
            ebcdic_bytes = bytearray(selected_text.encode('latin1'))
            # Decode EBCDIC bytes to ASCII
            ascii_string = ebcdic_bytes.decode('cp500', errors='replace')

            # Display the ASCII string in a prompt box allowing user to edit
            text_area = JTextArea(ascii_string, 20, 60)
            scroll_pane = JScrollPane(text_area)
            option = JOptionPane.showOptionDialog(None, scroll_pane, "EBCDIC -> ASCII", JOptionPane.OK_CANCEL_OPTION, JOptionPane.PLAIN_MESSAGE, None, None, None)

            if option == JOptionPane.OK_OPTION:
                edited_ascii = text_area.getText()
                # Convert edited ASCII back to EBCDIC bytes
                edited_ebcdic_bytes = bytearray(edited_ascii.encode('cp500'))
                stripped_chars_bytes = bytearray(stripped_chars.encode('latin1'))

                # Combine the EBCDIC bytes and the stripped last two characters
                final_ebcdic_bytes = edited_ebcdic_bytes + stripped_chars_bytes

                # Display the final raw data directly in the same JTextArea
                final_raw_string = final_ebcdic_bytes.decode('latin1')
                text_area.setText(final_raw_string)
                scroll_pane = JScrollPane(text_area)
                JOptionPane.showMessageDialog(None, scroll_pane, "ASCII -> EBCDIC", JOptionPane.PLAIN_MESSAGE)
                print("ASCII -> EBCDIC:\n", final_raw_string)
        except Exception as e:
            error_message = "Error processing EBCDIC Data: %s" % str(e)
            self._callbacks.issueAlert(error_message)
            print(error_message)
