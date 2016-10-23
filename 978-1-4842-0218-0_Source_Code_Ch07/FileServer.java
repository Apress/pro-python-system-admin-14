import java.io.*;
import java.util.*;
import java.text.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class FileServer extends HttpServlet {

    public void doGet(HttpServletRequest request, HttpServletResponse response)
    throws IOException, ServletException
    {
        response.setContentType("text/html");
        PrintWriter out = response.getWriter();

        out.println(System.getProperty("user.dir") + "<br/>");

        String fileName = request.getParameter("fn");
        if (fileName != null) {
            out.println("File name: " + fileName);
            out.println("<hr/>");
            out.println(readFile(fileName));
        } else {
            out.println("No file specified");
        }

    }

    private String readFile(String file) throws IOException {
        StringBuilder stringBuilder = new StringBuilder();
        Scanner scanner = new Scanner(new BufferedReader(new FileReader(file)));

        try {
            while(scanner.hasNextLine()) {        
                stringBuilder.append(scanner.nextLine() + "\n");
            }
        } finally {
            scanner.close();
        }
        return stringBuilder.toString();
    }
}

