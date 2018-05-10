import { Component } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Observable } from 'rxjs';
import 'rxjs/add/operator/toPromise';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  private title = 'app';
  private base_url: string = "http://localhost:8000";

  private specie_id: string = "9606";
  private amino_acid_sequence: string = "ATCDQYWEGLFHYKIRPHVVVPYQM";
  private primer_length: string = "12";
  private email: string = "shiv.prsd19@gmail.com";

  private specie_data = {
      id: '',
      head: '',
      data: []
  };

  // constructor(private http: Http){}

  public fetchSpeciesData(){
      if(this.specie_id.trim() != ""){
          let url = this.base_url + "/api/load-species-data/?specie_id=" + this.specie_id;
          this.http.get(url).toPromise().then((res)=>{
            console.log(res);
          }).catch((err)=>{
            console.log(err)
          });
      }
  }
  // public runApp(){
  //
  //     let url = this.base_url + "/api/run-app/?amino_acid_seq=" + this.amino_acid_sequence + "&email=" + this.email + "&primer_len=" + this.primer_length + "&specie_id="+this.specie_id;
  //
  //     this.http.get(url)
  //       .toPromise()
  //       .then((res)=>{
  //         console.log(res);
  //       }).catch((err) => {
  //         console.log(err)
  //       });
  //
  // }
}
