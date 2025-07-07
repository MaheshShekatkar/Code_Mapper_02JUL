import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { MultiSelect } from "react-multi-select-component";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import "mermaid/dist/mermaid.min.css";
import mermaid from "mermaid";

const App = () => {
  const [options, setOptions] = useState([]);
  const [selected, setSelected] = useState([]);
  const [markdown, setMarkdown] = useState("## Hello Markdown\n\n```mermaid\ngraph TD;\n  A-->B;\n  A-->C;\n  B-->D;\n  C-->D;\n```\n");

  useEffect(() => {
    fetch("/api/dependencies")
      .then((res) => res.json())
      .then((data) => {
        const formattedOptions = data.map(dep => ({ label: dep.name, value: dep.id }));
        setOptions(formattedOptions);

        // Generate markdown table
        let table = "| ID | Name |\n|----|------|\n";
        data.forEach(dep => {
          table += `| ${dep.id} | ${dep.name} |\n`;
        });

        setMarkdown(prev => prev + "\n" + table);
      });
  }, []);

  useEffect(() => {
    mermaid.initialize({ startOnLoad: false });
    const mermaidElements = document.querySelectorAll(".language-mermaid");
    mermaidElements.forEach((element, index) => {
      const renderTarget = document.createElement("div");
      renderTarget.id = `mermaid-${index}`;
      element.parentNode.replaceChild(renderTarget, element);
      try {
        mermaid.render(`mermaid-svg-${index}`, element.textContent, (svgCode) => {
          renderTarget.innerHTML = svgCode;
        });
      } catch (e) {
        renderTarget.innerHTML = "<pre>Error rendering Mermaid diagram</pre>";
      }
    });
  }, [markdown]);

  return (
    <div className="p-6 space-y-6">
      <Card>
        <CardContent className="pt-4">
          <h2 className="text-xl font-bold mb-2">Select Dependencies</h2>
          <MultiSelect
            options={options}
            value={selected}
            onChange={setSelected}
            labelledBy="Select"
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <h2 className="text-xl font-bold mb-2">Markdown Input</h2>
          <textarea
            className="w-full h-40 border rounded p-2"
            value={markdown}
            onChange={(e) => setMarkdown(e.target.value)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-4">
          <h2 className="text-xl font-bold mb-2">Rendered Output</h2>
          <div className="prose max-w-none">
            <ReactMarkdown
              children={markdown}
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default App;